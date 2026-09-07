# repos/terraform-medquad-dev/load_balancer_iap.tf
# Enterprise Ingress Architecture: External HTTPS Application Load Balancer + Serverless NEG + Google-Managed SSL + IAP

# 1. Global Static Anycast IPv4 Address
resource "google_compute_global_address" "medquad_global_ip" {
  name        = "medquad-global-ip"
  description = "Global Anycast IP for MedQuAD HTTPS Load Balancer"
  project     = module.project_admin.project_id
}

# 2. Serverless Network Endpoint Group (Serverless NEG) pointing to Cloud Run
resource "google_compute_region_network_endpoint_group" "medquad_serverless_neg" {
  name                  = "medquad-serverless-neg-${var.environment}"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = module.project_admin.project_id

  cloud_run {
    service = google_cloud_run_v2_service.medquad_backend.name
  }
}

# 3. Global External Managed Backend Service
resource "google_compute_backend_service" "medquad_backend_service" {
  name                  = "medquad-backend-service"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  project               = module.project_admin.project_id

  backend {
    group = google_compute_region_network_endpoint_group.medquad_serverless_neg.id
  }

  dynamic "iap" {
    for_each = var.enable_iap ? [1] : []
    content {
      oauth2_client_id     = var.iap_client_id
      oauth2_client_secret = var.iap_client_secret
    }
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }
}

# 4. Global URL Map (HTTPS Traffic Routing)
resource "google_compute_url_map" "medquad_url_map" {
  name            = "medquad-url-map"
  default_service = google_compute_backend_service.medquad_backend_service.id
  project         = module.project_admin.project_id
}

# 5. Google-Managed SSL Certificate for Custom Domain
resource "google_compute_managed_ssl_certificate" "medquad_ssl_cert" {
  name    = "medquad-ssl-cert"
  project = module.project_admin.project_id

  managed {
    domains = [var.custom_domain_name]
  }
}

# 6. Target HTTPS Proxy
resource "google_compute_target_https_proxy" "medquad_https_proxy" {
  name             = "medquad-https-proxy"
  url_map          = google_compute_url_map.medquad_url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.medquad_ssl_cert.id]
  project          = module.project_admin.project_id
}

# 7. Global HTTPS Forwarding Rule (Port 443)
resource "google_compute_global_forwarding_rule" "medquad_https_forwarding" {
  name                  = "medquad-https-forwarding"
  target                = google_compute_target_https_proxy.medquad_https_proxy.id
  ip_address            = google_compute_global_address.medquad_global_ip.address
  port_range            = "443"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  project               = module.project_admin.project_id
}

# 8. HTTP to HTTPS Permanent Redirect URL Map
resource "google_compute_url_map" "medquad_http_redirect_map" {
  name    = "medquad-http-redirect-map"
  project = module.project_admin.project_id

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

# 9. Target HTTP Proxy for Redirect
resource "google_compute_target_http_proxy" "medquad_http_proxy" {
  name    = "medquad-http-proxy"
  url_map = google_compute_url_map.medquad_http_redirect_map.id
  project = module.project_admin.project_id
}

# 10. Global HTTP Forwarding Rule (Port 80)
resource "google_compute_global_forwarding_rule" "medquad_http_forwarding" {
  name                  = "medquad-http-forwarding"
  target                = google_compute_target_http_proxy.medquad_http_proxy.id
  ip_address            = google_compute_global_address.medquad_global_ip.address
  port_range            = "80"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  project               = module.project_admin.project_id
}

# 11. IAM: Grant IAP Access to Clinical Researchers
resource "google_iap_web_backend_service_iam_member" "clinical_researchers_iap_access" {
  count               = var.enable_iap ? 1 : 0
  project             = module.project_admin.project_id
  web_backend_service = google_compute_backend_service.medquad_backend_service.name
  role                = "roles/iap.httpsResourceAccessor"
  member              = "group:${var.clinical_researchers_group}"
}

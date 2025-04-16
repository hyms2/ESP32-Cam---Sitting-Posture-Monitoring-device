#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#define UBIDOTS_TOKEN "BBUS-6aSAWrXfWWuBGe7tMiw0tvMpdSt1CD" // <-- Replace with your real token
#define DEVICE_LABEL "esp-32"      // Name for this ESP32
#define VARIABLE_LABEL "posture_score"     // Name of the variable in Ubidots

const char* ubidots_server = "http://industrial.api.ubidots.com/api/v1.6/devices/" DEVICE_LABEL;


// Replace with your Wi-Fi info
const char* ssid = "**";
const char* password = "**";

// Your Flask server IP
const char* serverName = "http://192.168.68.103:5000/upload";  // Replace with your PC IP

void startCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.pin_xclk = 0;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 10;
  config.fb_count = 1;

  // Init with config
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.println("Camera init failed");
    return;
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("Connected to WiFi");
  startCamera();
}

void loop() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  HTTPClient http;
  http.begin(serverName);
  http.addHeader("Content-Type", "image/jpeg");
  int httpResponseCode = http.POST(fb->buf, fb->len);

  if (httpResponseCode > 0) {
  String response = http.getString();
  Serial.println(response);

  int scoreIndex = response.indexOf("\"score\":");
  if (scoreIndex >= 0) {
    float postureScore = response.substring(scoreIndex + 8).toFloat();

    if (!isnan(postureScore)) {
      HTTPClient ubidots;
      String payload = "{\"" VARIABLE_LABEL "\":" + String(postureScore, 2) + "}";

      ubidots.begin(ubidots_server);
      ubidots.addHeader("Content-Type", "application/json");
      ubidots.addHeader("X-Auth-Token", UBIDOTS_TOKEN);
      int statusCode = ubidots.POST(payload);

      if (statusCode > 0) {
        Serial.println("✅ Sent to Ubidots: " + String(statusCode));
      } else {
        Serial.println("❌ Failed to send to Ubidots");
      }

      ubidots.end();
    }
  }
} else {
  Serial.printf("Error: %s\n", http.errorToString(httpResponseCode).c_str());
}



  http.end();
  esp_camera_fb_return(fb);

  delay(2000); // Wait 10s before next capture
}
import type { ExpoConfig } from "expo/config";

const config: ExpoConfig = {
  name: process.env.EXPO_PUBLIC_APP_NAME ?? "DentalCare",
  slug: "dentalcare-clinicos",
  scheme: "dentalcare",
  version: "0.1.0",
  orientation: "portrait",
  userInterfaceStyle: "light",
  newArchEnabled: true,
  plugins: ["expo-router", "expo-secure-store", "expo-camera", "expo-notifications", ["expo-image-picker", { photosPermission: "Select a document or image to share securely with your clinic." }]],
  android: { package: "com.dentalcare.clinicos", permissions: ["CAMERA", "POST_NOTIFICATIONS"] },
  experiments: { typedRoutes: true },
};

export default config;

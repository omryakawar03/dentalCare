import "../global.css";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AppProvider } from "@/providers/app-provider";

export default function RootLayout() {
  return <AppProvider><StatusBar style="dark"/><Stack screenOptions={{headerShown:false}}><Stack.Screen name="index"/><Stack.Screen name="(app)"/></Stack></AppProvider>;
}

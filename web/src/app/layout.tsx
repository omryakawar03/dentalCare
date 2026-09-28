import type { Metadata } from "next";
import "./globals.css";
import { StoreProvider } from "@/providers/store-provider";

const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "DentalCare";

export const metadata: Metadata = {
  title: `${appName} | Clinic operations`,
  description: "Secure, multi-clinic dental practice management",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><StoreProvider>{children}</StoreProvider></body></html>;
}

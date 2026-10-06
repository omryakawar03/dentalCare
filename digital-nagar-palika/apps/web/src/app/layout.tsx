import type { Metadata } from "next";
import "./style.css";
export const metadata: Metadata = { title: "Digital Nagar Palika", description: "Municipal services and public information" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="mr"><body>{children}</body></html>;
}

import "./globals.css";
import AppLayout from "@/components/AppLayout";

export const metadata = {
  title: "StatKarmaYogi - Continuous AI Competency Intelligence Platform",
  description: "AI-Powered Skill Intelligence, Dynamic Gap Analysis, Continuous Learning Loop & Groq Cloud Technical Mentor",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-slate-900 antialiased">
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}

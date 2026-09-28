import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";

const credentialsSchema = z.object({ email: z.email(), password: z.string().min(1).max(256) });
const apiUrl = process.env.CLINIC_API_URL ?? "http://localhost:8000/api/v1";
const secure = process.env.NODE_ENV === "production";
const cookieBase = { httpOnly: true, secure, sameSite: "strict" as const, path: "/" };

async function post(path: string, body: unknown) {
  return fetch(`${apiUrl}${path}`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), cache: "no-store",
  });
}

export async function POST(request: NextRequest) {
  if (request.headers.get("origin") !== request.nextUrl.origin) {
    return NextResponse.json({ error: "Invalid request origin." }, { status: 403 });
  }
  const parsed = credentialsSchema.safeParse(await request.json().catch(() => null));
  if (!parsed.success) return NextResponse.json({ error: "Enter a valid email and password." }, { status: 400 });
  try {
    const upstream = await post("/auth/login", parsed.data);
    const body = await upstream.json();
    if (!upstream.ok || !body?.data?.access_token || !body?.data?.refresh_token) {
      return NextResponse.json({ error: "We couldn’t sign you in. Check your details and try again." }, { status: upstream.status === 429 ? 429 : 401 });
    }
    const response = NextResponse.json({ success: true });
    response.cookies.set("clinic_access", body.data.access_token, { ...cookieBase, maxAge: body.data.expires_in });
    response.cookies.set("clinic_refresh", body.data.refresh_token, { ...cookieBase, maxAge: 60 * 60 * 24 * 30 });
    response.headers.set("Cache-Control", "no-store");
    return response;
  } catch {
    return NextResponse.json({ error: "Sign-in is temporarily unavailable." }, { status: 503 });
  }
}

export async function GET(request: NextRequest) {
  const access = request.cookies.get("clinic_access")?.value;
  if (!access) return NextResponse.json({ error: "Unauthenticated" }, { status: 401 });
  try {
    let upstream = await fetch(`${apiUrl}/auth/me`, { headers: { Authorization: `Bearer ${access}` }, cache: "no-store" });
    let rotated: { access_token: string; refresh_token: string; expires_in: number } | null = null;
    if (upstream.status === 401) {
      const refresh = request.cookies.get("clinic_refresh")?.value;
      if (!refresh) return clearCookies(NextResponse.json({ error: "Unauthenticated" }, { status: 401 }));
      const refreshResponse = await post("/auth/refresh", { refresh_token: refresh });
      const tokens = await refreshResponse.json();
      if (!refreshResponse.ok || !tokens?.data?.access_token || !tokens?.data?.refresh_token) {
        return clearCookies(NextResponse.json({ error: "Session expired" }, { status: 401 }));
      }
      rotated = tokens.data;
      upstream = await fetch(`${apiUrl}/auth/me`, { headers: { Authorization: `Bearer ${tokens.data.access_token}` }, cache: "no-store" });
    }
    const body = await upstream.json();
    if (!upstream.ok) return clearCookies(NextResponse.json({ error: "Unauthenticated" }, { status: 401 }));
    const result = NextResponse.json(body.data, { headers: { "Cache-Control": "no-store" } });
    if (rotated) {
      result.cookies.set("clinic_access", rotated.access_token, { ...cookieBase, maxAge: rotated.expires_in });
      result.cookies.set("clinic_refresh", rotated.refresh_token, { ...cookieBase, maxAge: 60 * 60 * 24 * 30 });
    }
    return result;
  } catch {
    return NextResponse.json({ error: "Session service unavailable" }, { status: 503 });
  }
}

export async function DELETE(request: NextRequest) {
  if (request.headers.get("origin") !== request.nextUrl.origin) {
    return NextResponse.json({ error: "Invalid request origin." }, { status: 403 });
  }
  const access = request.cookies.get("clinic_access")?.value;
  if (access) await fetch(`${apiUrl}/auth/logout`, { method: "POST", headers: { Authorization: `Bearer ${access}` }, cache: "no-store" }).catch(() => undefined);
  return clearCookies(NextResponse.json({ success: true }));
}

function clearCookies(response: NextResponse) {
  response.cookies.set("clinic_access", "", { ...cookieBase, maxAge: 0 });
  response.cookies.set("clinic_refresh", "", { ...cookieBase, maxAge: 0 });
  return response;
}

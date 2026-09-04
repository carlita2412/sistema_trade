import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const url = process.env.LIGHTSAIL_API_URL;
  const secret = process.env.LIGHTSAIL_API_SECRET;

  if (!url) {
    return NextResponse.json({ status: "error", error: "LIGHTSAIL_API_URL no está configurada" }, { status: 500 });
  }

  try {
    const res = await fetch(url, {
      headers: secret ? { "X-API-Key": secret } : undefined,
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e: any) {
    return NextResponse.json({ status: "error", error: `No se pudo contactar Lightsail: ${e.message}` }, { status: 502 });
  }
}

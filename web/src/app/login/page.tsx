"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const schema = z.object({ email: z.email("Enter a valid email address"), password: z.string().min(1, "Enter your password") });
type FormValues = z.infer<typeof schema>;
const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "DentalCare";

export default function LoginPage() {
  const router = useRouter();
  const [serverError, setServerError] = useState("");
  const [isSubmitting, setSubmitting] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const submit = async (values: FormValues) => {
    setSubmitting(true); setServerError("");
    try {
      const response = await fetch("/api/session", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(values) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error ?? "Sign-in failed");
      router.replace("/"); router.refresh();
    } catch (error) { setServerError(error instanceof Error ? error.message : "Sign-in is temporarily unavailable."); }
    finally { setSubmitting(false); }
  };
  return <main className="login-page"><form className="login-card" onSubmit={handleSubmit(submit)}>
    <div className="brand"><span className="brand-mark">✦</span><span>{appName}</span></div>
    <div className="eyebrow">SECURE CLINIC WORKSPACE</div><h1>Welcome back</h1><p className="subtitle">Sign in to your clinic workspace.</p>
    <label className="field-label" htmlFor="email">Email address</label><input id="email" autoComplete="username" inputMode="email" className="login-input" {...register("email")}/>
    {errors.email && <p className="field-error">{errors.email.message}</p>}
    <label className="field-label" htmlFor="password">Password</label><input id="password" type="password" autoComplete="current-password" className="login-input" {...register("password")}/>
    {errors.password && <p className="field-error">{errors.password.message}</p>}
    {serverError && <p role="alert" className="field-error">{serverError}</p>}
    <button className="button-primary login-button" disabled={isSubmitting}>{isSubmitting ? "Signing in…" : "Sign in"}</button>
    <p className="login-note">Your access is limited to the clinics and records assigned to your account.</p>
  </form></main>;
}

import { useState } from "react";
import { Text, TextInput, Pressable, View, KeyboardAvoidingView, Platform } from "react-native";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { router } from "expo-router";
import { useLoginMutation } from "@/features/auth/auth-api";
import { appName } from "@/constants/brand";

const schema = z.object({ email: z.email(), password: z.string().min(1, "Enter your password") });
type FormValues = z.infer<typeof schema>;

export default function SignInScreen() {
  const [login, { isLoading }] = useLoginMutation();
  const [serverError, setServerError] = useState("");
  const { control, handleSubmit, formState: { errors } } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { email: "", password: "" } });
  const submit = async (values: FormValues) => {
    setServerError("");
    try { await login(values).unwrap(); router.replace("/(app)/home"); }
    catch { setServerError("We couldn’t sign you in. Check your details and try again."); }
  };
  return <KeyboardAvoidingView className="flex-1 bg-clinic-canvas justify-center px-6" behavior={Platform.OS === "ios" ? "padding" : undefined}>
    <View className="w-full max-w-md self-center rounded-2xl bg-white p-6 shadow-sm">
      <View className="mb-7 flex-row items-center gap-3"><View className="h-11 w-11 items-center justify-center rounded-xl bg-clinic-teal"><Text className="text-xl font-bold text-white">✦</Text></View><View><Text className="text-xl font-bold text-clinic-ink">{appName}</Text><Text className="mt-1 text-xs text-slate-500">Clinic operations</Text></View></View>
      <Text className="text-2xl font-bold text-clinic-ink">Welcome back</Text><Text className="mb-6 mt-2 text-sm text-slate-500">Sign in to your clinic workspace.</Text>
      <Text className="mb-2 text-xs font-semibold text-slate-700">Email</Text>
      <Controller control={control} name="email" render={({field:{onChange,onBlur,value}})=><TextInput accessibilityLabel="Email address" autoCapitalize="none" keyboardType="email-address" onBlur={onBlur} onChangeText={onChange} value={value} className="mb-1 rounded-lg border border-slate-200 px-3 py-3 text-sm" placeholder="you@clinic.com"/>}/>
      {errors.email && <Text className="mb-3 text-xs text-red-700">{errors.email.message}</Text>}
      <Text className="mb-2 mt-3 text-xs font-semibold text-slate-700">Password</Text>
      <Controller control={control} name="password" render={({field:{onChange,onBlur,value}})=><TextInput accessibilityLabel="Password" secureTextEntry onBlur={onBlur} onChangeText={onChange} value={value} className="rounded-lg border border-slate-200 px-3 py-3 text-sm" placeholder="Enter your password"/>}/>
      {errors.password && <Text className="mt-1 text-xs text-red-700">{errors.password.message}</Text>}
      {!!serverError && <Text accessibilityRole="alert" className="mt-3 text-sm text-red-700">{serverError}</Text>}
      <Pressable accessibilityRole="button" disabled={isLoading} onPress={handleSubmit(submit)} className="mt-6 items-center rounded-lg bg-clinic-teal py-3.5"><Text className="font-semibold text-white">{isLoading ? "Signing in…" : "Sign in"}</Text></Pressable>
      <Text className="mt-5 text-center text-xs leading-5 text-slate-400">Access is limited to the clinics and records assigned to your account.</Text>
    </View>
  </KeyboardAvoidingView>;
}

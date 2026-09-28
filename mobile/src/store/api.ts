import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from "@reduxjs/toolkit/query";
import * as SecureStore from "expo-secure-store";

const rawBaseQuery = fetchBaseQuery({
  baseUrl: process.env.EXPO_PUBLIC_API_URL ?? "http://10.0.2.2:8000/api/v1",
  prepareHeaders: async (headers) => {
    const token = await SecureStore.getItemAsync("access_token");
    if (token) headers.set("authorization", `Bearer ${token}`);
    return headers;
  },
});

type Tokens = { access_token: string; refresh_token: string; expires_in: number };
type Envelope<T> = { success: true; data: T };
let refreshInFlight: Promise<boolean> | null = null;

const baseQueryWithRefresh: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (args, apiContext, extraOptions) => {
  let result = await rawBaseQuery(args, apiContext, extraOptions);
  const url = typeof args === "string" ? args : args.url;
  if (result.error?.status !== 401 || url.includes("/auth/refresh")) return result;

  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const refreshToken = await SecureStore.getItemAsync("refresh_token");
      if (!refreshToken) return false;
      const refreshed = await rawBaseQuery({ url: "/auth/refresh", method: "POST", body: { refresh_token: refreshToken } }, apiContext, extraOptions);
      const tokens = (refreshed.data as Envelope<Tokens> | undefined)?.data;
      if (!tokens?.access_token || !tokens.refresh_token) return false;
      await SecureStore.setItemAsync("access_token", tokens.access_token);
      await SecureStore.setItemAsync("refresh_token", tokens.refresh_token);
      return true;
    })().finally(() => { refreshInFlight = null; });
  }
  const refreshed = await refreshInFlight;
  if (refreshed) result = await rawBaseQuery(args, apiContext, extraOptions);
  else {
    await SecureStore.deleteItemAsync("access_token");
    await SecureStore.deleteItemAsync("refresh_token");
  }
  return result;
};

export const api = createApi({
  reducerPath: "api",
  baseQuery: baseQueryWithRefresh,
  tagTypes: ["Clinic", "Patient", "Appointment"],
  endpoints: () => ({}),
});

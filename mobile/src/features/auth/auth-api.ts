import * as SecureStore from "expo-secure-store";
import { api } from "@/store/api";

type Envelope<T> = { success: true; data: T; message?: string };
export type TokenPair = { access_token: string; refresh_token: string; token_type: "bearer"; expires_in: number };

export const authApi = api.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<TokenPair, { email: string; password: string }>({
      query: (body) => ({ url: "/auth/login", method: "POST", body }),
      transformResponse: (response: Envelope<TokenPair>) => response.data,
      async onQueryStarted(_, { queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          await SecureStore.setItemAsync("access_token", data.access_token);
          await SecureStore.setItemAsync("refresh_token", data.refresh_token);
        } catch { /* The form presents the API error without persisting a partial session. */ }
      },
    }),
  }),
});

export const { useLoginMutation } = authApi;

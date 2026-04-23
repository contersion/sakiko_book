import { apiClient } from "./client";
import type { LoginPayload, TokenResponse, User } from "../types/api";

export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
}

export const authApi = {
  login(payload: LoginPayload) {
    return apiClient.post<TokenResponse>("/api/auth/login", payload, {
      auth: false,
    });
  },
  getCurrentUser() {
    return apiClient.get<User>("/api/auth/me");
  },
  changePassword(payload: ChangePasswordPayload) {
    return apiClient.post<{ message: string }>("/api/auth/change-password", payload);
  },
};

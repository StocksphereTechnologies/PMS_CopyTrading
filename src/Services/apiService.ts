// src/services/apiService.ts

import axios, { AxiosRequestConfig, Method } from 'axios'

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'

interface ApiOptions {
  method?: HttpMethod
  body?: Record<string, any>
  params?: Record<string, any>
  headers?: Record<string, string>
}

export const httpClient = async <T>(
  endpoint: string,
  options: ApiOptions = {},
): Promise<T> => {
  const { method = 'GET', body, params, headers } = options

  const config: AxiosRequestConfig = {
    url: `${endpoint}`,
    method: method as Method,
    params,
    data: body,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    withCredentials: false, // set to true if you're sending cookies
  }

  try {
    const response = await axios.request<T>(config)
    return response.data
  } catch (error: any) {
    const message =
      error?.response?.data?.message ||
      `API Error: ${error?.response?.status} ${error?.response?.statusText}`
    throw new Error(message)
  }
}

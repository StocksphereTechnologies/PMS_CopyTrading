import { create } from 'zustand';

export interface Account {
  account_id: number;
  owner_id: number;
  broker_name: string;
  nickname?: string;
  trading_login_id: string;
  is_enabled: boolean;
  is_validated: boolean;
  is_paid: boolean;
  token_generated_at?: string;
  created_at: string;
  updated_at: string;
}

interface AccountState {
  accounts: Account[];
  loading: boolean;
  error: string | null;
  
  // Actions
  setAccounts: (accounts: Account[]) => void;
  addAccount: (account: Account) => void;
  updateAccount: (accountId: number, updates: Partial<Account>) => void;
  removeAccount: (accountId: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearAccounts: () => void;
}

export const useAccountStore = create<AccountState>((set) => ({
  accounts: [],
  loading: false,
  error: null,
  
  setAccounts: (accounts) => set({ accounts, error: null }),
  
  addAccount: (account) => set((state) => ({
    accounts: [...state.accounts, account]
  })),
  
  updateAccount: (accountId, updates) => set((state) => ({
    accounts: state.accounts.map(acc =>
      acc.account_id === accountId ? { ...acc, ...updates } : acc
    )
  })),
  
  removeAccount: (accountId) => set((state) => ({
    accounts: state.accounts.filter(acc => acc.account_id !== accountId)
  })),
  
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  clearAccounts: () => set({ accounts: [], error: null }),
}));

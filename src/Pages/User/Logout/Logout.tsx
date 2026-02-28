import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { message, Spin } from 'antd';
import { authService } from '../../../Services/authService';
import { useAuthStore } from '../../../store/authStore';
import { useAccountStore } from '../../../store/accountStore';

const Logout: React.FC = () => {
  const navigate = useNavigate();
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const clearAccounts = useAccountStore((state) => state.clearAccounts);

  useEffect(() => {
    const performLogout = async () => {
      try {
        await authService.logout();
      } catch (error) {
        // Ignore errors, clear local state anyway
      } finally {
        clearAuth();
        clearAccounts();
        message.success('Logged out successfully');
        navigate('/login');
      }
    };

    performLogout();
  }, [clearAuth, clearAccounts, navigate]);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh' 
    }}>
      <Spin size="large" tip="Logging out..." />
    </div>
  );
};

export default Logout;


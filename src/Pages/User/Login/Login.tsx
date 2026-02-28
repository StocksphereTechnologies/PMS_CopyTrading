import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Row, Col } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../../Services/authService';
import { useAuthStore } from '../../../store/authStore';

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      // Login
      const loginResponse = await authService.login(values);
      
      // Save to store (loginResponse already contains user details)
      const { access_token, ...userData } = loginResponse as any;
      setAuth(userData, access_token);
      
      message.success('Login successful!');
      navigate('/trading/portfolio');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Login failed';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Row justify="center" style={{ width: '100%' }}>
        <Col xs={22} sm={18} md={12} lg={8} xl={6}>
          <Card 
            title={
              <div style={{ textAlign: 'center', fontSize: 24, fontWeight: 600, color: '#00a6a6' }}>
                Login to StockSphere
              </div>
            }
            variant="borderless"
            style={{ 
              borderRadius: 12,
              boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
            }}
          >
            <Form onFinish={onFinish} layout="vertical" size="large">
              <Form.Item
                label="Email"
                name="email"
                rules={[
                  { required: true, message: 'Please input your email!' },
                  { type: 'email', message: 'Please enter a valid email!' }
                ]}
              >
                <Input 
                  prefix={<UserOutlined />}
                  placeholder="your@email.com" 
                />
              </Form.Item>

              <Form.Item
                label="Password"
                name="password"
                rules={[{ required: true, message: 'Please input your password!' }]}
              >
                <Input.Password 
                  prefix={<LockOutlined />}
                  placeholder="Password" 
                />
              </Form.Item>

              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading} 
                  block
                  style={{
                    height: 45,
                    fontSize: 16,
                    fontWeight: 600,
                    background: '#00a6a6',
                    borderColor: '#00a6a6'
                  }}
                >
                  Login
                </Button>
              </Form.Item>

              <div style={{ textAlign: 'center', marginTop: 16 }}>
                Don't have an account? <a href="/signup" style={{ color: '#00a6a6', fontWeight: 600 }}>Sign up</a>
              </div>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Login;

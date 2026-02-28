import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Row, Col } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined, EnvironmentOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../../Services/authService';
import { useAuthStore } from '../../../store/authStore';

const Signup: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const response = await authService.signup(values);
      
      // Auto-login after signup
      setAuth({
        user_id: response.user_id,
        email: response.email,
        full_name: response.full_name,
        phone_number: response.phone_number,
        city: response.city,
        state: response.state,
        country: response.country,
        is_active: response.is_active,
      }, response.access_token);
      
      message.success('Account created successfully!');
      navigate('/trading/portfolio');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Signup failed';
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
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px 0'
    }}>
      <Row justify="center" style={{ width: '100%' }}>
        <Col xs={22} sm={20} md={16} lg={12} xl={10}>
          <Card 
            title={
              <div style={{ textAlign: 'center', fontSize: 24, fontWeight: 600, color: '#00a6a6' }}>
                Create Your Account
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
                label="Full Name"
                name="full_name"
                rules={[{ required: true, message: 'Please input your name!' }]}
              >
                <Input 
                  prefix={<UserOutlined />}
                  placeholder="John Doe" 
                />
              </Form.Item>

              <Form.Item
                label="Email"
                name="email"
                rules={[
                  { required: true, message: 'Please input your email!' },
                  { type: 'email', message: 'Please enter a valid email!' }
                ]}
              >
                <Input 
                  prefix={<MailOutlined />}
                  placeholder="your@email.com" 
                />
              </Form.Item>

              <Form.Item
                label="Password"
                name="password"
                rules={[
                  { required: true, message: 'Please input your password!' },
                  { min: 8, message: 'Password must be at least 8 characters!' }
                ]}
              >
                <Input.Password 
                  prefix={<LockOutlined />}
                  placeholder="Minimum 8 characters" 
                />
              </Form.Item>

              <Form.Item
                label="Phone Number (Optional)"
                name="phone_number"
              >
                <Input 
                  prefix={<PhoneOutlined />}
                  placeholder="+91-9876543210" 
                />
              </Form.Item>

              <Form.Item
                label="City (Optional)"
                name="city"
              >
                <Input 
                  prefix={<EnvironmentOutlined />}
                  placeholder="Mumbai" 
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
                  Sign Up
                </Button>
              </Form.Item>

              <div style={{ textAlign: 'center', marginTop: 16 }}>
                Already have an account? <a href="/login" style={{ color: '#00a6a6', fontWeight: 600 }}>Login</a>
              </div>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Signup;

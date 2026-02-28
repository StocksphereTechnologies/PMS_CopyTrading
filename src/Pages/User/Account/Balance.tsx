import React, { useState } from "react";
import { Card, Row, Col } from "antd";
import { ExpandOutlined, CompressOutlined } from "@ant-design/icons";

const Balance: React.FC = () => {
  const [isFullScreen, setIsFullScreen] = useState(false);

  const cardStyle: React.CSSProperties = {
    borderRadius: "8px",
    color: "#fff",
    fontWeight: 600,
    minHeight: "100px",
    padding: "16px",
  };

  const valueStyle: React.CSSProperties = {
    fontSize: "20px",
    fontWeight: 700,
  };

  const iconStyle: React.CSSProperties = {
    fontSize: "48px",
    opacity: 0.6,
    lineHeight: 1,
  };

  return (
    <div style={{ padding: "16px" }}>
      {/* Outer container card (with header + expand/minimize) */}
      <Card
        title="Balance"
        extra={
          isFullScreen ? (
            <CompressOutlined
              style={{ cursor: "pointer", fontSize: "18px" }}
              onClick={() => setIsFullScreen(false)}
            />
          ) : (
            <ExpandOutlined
              style={{ cursor: "pointer", fontSize: "18px" }}
              onClick={() => setIsFullScreen(true)}
            />
          )
        }
        style={{
          borderRadius: "8px",
          transition: "all 0.3s ease-in-out",
          position: isFullScreen ? "fixed" : "relative",
          top: isFullScreen ? 0 : "auto",
          left: isFullScreen ? 0 : "auto",
          width: isFullScreen ? "100vw" : "auto",
          height: isFullScreen ? "100vh" : "auto",
          zIndex: isFullScreen ? 1000 : "auto",
        }}
        bodyStyle={{
          height: isFullScreen ? "calc(100vh - 60px)" : "auto",
          overflowY: "auto",
        }}
      >
        <Row gutter={[16, 16]}>
          {/* Balance */}
          <Col xs={24} sm={12} md={12} lg={12}>
            <Card
              style={{
                ...cardStyle,
                background: "linear-gradient(90deg, #00c88f, #00e6a5)",
              }}
              bodyStyle={{ padding: 0 }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                }}
              >
                {/* Left side */}
                <div>
                  <div>Balance</div>
                  <div style={valueStyle}>₹0.00</div>
                </div>

                {/* Right side */}
                <div style={iconStyle}>₹</div>
              </div>
            </Card>
          </Col>

          {/* Awaiting Approval */}
          <Col xs={24} sm={12} md={12} lg={12}>
            <Card
              style={{
                ...cardStyle,
                background: "linear-gradient(90deg, #ff9574, #ffb8a2)",
              }}
              bodyStyle={{ padding: 0 }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                }}
              >
                <div>
                  <div>Awaiting Approval</div>
                  <div style={valueStyle}>₹0.00</div>
                </div>
                <div style={iconStyle}>₹</div>
              </div>
            </Card>
          </Col>

          {/* Total Lifetime Billing */}
          <Col xs={24} sm={12} md={12} lg={12}>
            <Card
              style={{
                ...cardStyle,
                background: "linear-gradient(90deg, #00acc1, #00e0fc)",
              }}
              bodyStyle={{ padding: 0 }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                }}
              >
                <div>
                  <div>Total Lifetime Billing</div>
                  <div style={valueStyle}>₹0.00</div>
                </div>
                <div style={iconStyle}>₹</div>
              </div>
            </Card>
          </Col>

          {/* Total Savings */}
          <Col xs={24} sm={12} md={12} lg={12}>
            <Card
              style={{
                ...cardStyle,
                background: "linear-gradient(90deg, #169bab, #00e0fc)",
              }}
              bodyStyle={{ padding: 0 }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                }}
              >
                <div>
                  <div>Total Savings (Discount)</div>
                  <div style={valueStyle}>₹0.00</div>
                </div>
                <div style={iconStyle}>₹</div>
              </div>
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Balance;

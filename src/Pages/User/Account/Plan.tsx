import React from "react";
import { Card } from "antd";
import { PushpinOutlined, RocketOutlined } from "@ant-design/icons";

const Plan: React.FC = () => {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        padding: 24,
        background: "linear-gradient(90deg, #2f3d4c 0%, #c7d1d8 50%, #2f3d4c 100%)",
        minHeight: "90vh",
      }}
    >
      <div style={{ width: 420, maxWidth: "100%" }}>
        {/* Header */}
        <div
          style={{
            background: "#00b3ad",
            color: "#fff",
            textAlign: "center",
            padding: "12px 16px",
            borderTopLeftRadius: 8,
            borderTopRightRadius: 8,
            fontSize: 22,
            fontWeight: 700,
            letterSpacing: 0.5,
          }}
        >
          Billing Plan
        </div>

        {/* Card */}
        <Card
          styles={{ body: { padding: 0 } }}
          style={{
            borderTopLeftRadius: 0,
            borderTopRightRadius: 0,
            borderBottomLeftRadius: 8,
            borderBottomRightRadius: 8,
            overflow: "hidden",
          }}
        >
          {/* Current Plan */}
          <div
            style={{
              background: "#f0f6fd",
              padding: "10px 14px",
              fontWeight: 700,
              fontSize: 16,
              display: "flex",
              alignItems: "center",
              justifyContent: "center", 
              gap: 8,
              borderBottom: "1px solid #e0e0e0",
            }}
          >
            <PushpinOutlined style={{ color: "#ff4d4f" }} /> Current Plan
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              <tr>
                <td style={tdKey}>Plan</td>
                <td style={tdValue}>
                  <span style={{ color: "purple", fontWeight: 700 }}>REGULAR</span>
                </td>
              </tr>
              <tr>
                <td style={tdKey}>Monthly Price</td>
                <td style={tdValue}>495/-</td>
              </tr>
              <tr>
                <td style={tdKey}>Discount</td>
                <td style={tdValue}>0/-</td>
              </tr>
            </tbody>
          </table>

          {/* Next Plan Upgrade */}
          <div
              style={{
                background: "#fff9e6",
                padding: "10px 14px",
                fontWeight: 700,
                fontSize: 16,
                display: "flex",
                alignItems: "center",
                justifyContent: "center", 
                gap: 8,
                borderTop: "1px solid #e0e0e0",
                borderBottom: "1px solid #e0e0e0",
              }}
            >
              <RocketOutlined style={{ color: "#faad14" }} /> Next Plan Upgrade
          </div>


          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              <tr>
                <td style={tdKey}>Plan</td>
                <td style={tdValue}>
                  <span style={{ color: "#d4380d", fontWeight: 700 }}>PREMIUM</span>
                </td>
              </tr>
              <tr>
                <td style={tdKey}>Monthly Price</td>
                <td style={tdValue}>445/-</td>
              </tr>
              <tr>
                <td style={tdKey}>Discount</td>
                <td style={tdValue}>50/-</td>
              </tr>
              <tr>
                <td style={tdKey}>Applicable after</td>
                <td style={{ ...tdValue, color: "red", fontWeight: 700 }}>
                  25,000/-
                </td>
              </tr>
            </tbody>
          </table>

          {/* Lifetime Bill */}
          <div
            style={{
              background: "#00b3ad",
              color: "#fff",
              textAlign: "center",
              padding: "12px",
              fontWeight: 700,
              fontSize: 16,
            }}
          >
            Total Lifetime Bill: 0/-
          </div>

          {/* Bottom Note */}
          <div
            style={{
              padding: "12px 14px",
              textAlign: "center",
              fontSize: 14,
            }}
          >
            You have{" "}
            <span style={{ color: "red", fontWeight: 700 }}>25,000/-</span> billing
            left for the next plan upgrade.
          </div>
        </Card>
      </div>
    </div>
  );
};

const tdKey: React.CSSProperties = {
  padding: "10px 14px",
  borderBottom: "1px solid #f0f0f0",
  fontWeight: 600,
  width: "60%",
};

const tdValue: React.CSSProperties = {
  padding: "10px 14px",
  borderBottom: "1px solid #f0f0f0",
  textAlign: "right",
  fontWeight: 600,
  color: "#2b2b2b",
};

export default Plan;

import React, { useState, useEffect } from "react";
import {
  Slider,
  Button,
  Typography,
  Space,
  Table,
  Divider,
  Progress,
  Row,
  Col,
  Grid,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import {
  RocketOutlined,
  StopOutlined,
  ClockCircleOutlined,
  DeleteOutlined,
} from "@ant-design/icons";

const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

interface TableData {
  key: string;
  symbol: string;
  ltp: string;
  cumulativeVol: string;
  time: string;
  week: string;
  month: string;
  ob1m: string;
  obCandle1m: string;
  ob5m: string;
  obCandle5m: string;
  detectedAt: string;
}

const breakoutColumns: ColumnsType<TableData> = [
  { title: "", key: "index", width: 60, align: "center", render: (_: any, __: TableData, index: number) => index + 1 },
  { title: "Symbol", dataIndex: "symbol", key: "symbol" },
  { title: "LTP", dataIndex: "ltp", key: "ltp" },
  { title: "Cumulative Vol", dataIndex: "cumulativeVol", key: "cumulativeVol" },
  { title: "Breakout Time", dataIndex: "time", key: "time" },
  { title: "Week Breakout", dataIndex: "week", key: "week" },
  { title: "Month Breakout", dataIndex: "month", key: "month" },
  { title: "Bullish OB Zone (1m)", dataIndex: "ob1m", key: "ob1m" },
  { title: "OB Detection Candle (1m)", dataIndex: "obCandle1m", key: "obCandle1m" },
  { title: "Bullish OB Zone (5m)", dataIndex: "ob5m", key: "ob5m" },
  { title: "OB Detection Candle (5m)", dataIndex: "obCandle5m", key: "obCandle5m" },
  { title: "Detected At", dataIndex: "detectedAt", key: "detectedAt" },
];

const breakdownColumns: ColumnsType<TableData> = [
  { title: "", key: "index", width: 60, align: "center", render: (_: any, __: TableData, index: number) => index + 1 },
  { title: "Symbol", dataIndex: "symbol", key: "symbol" },
  { title: "LTP", dataIndex: "ltp", key: "ltp" },
  { title: "Cumulative Vol", dataIndex: "cumulativeVol", key: "cumulativeVol" },
  { title: "Breakdown Time", dataIndex: "time", key: "time" },
  { title: "Week Breakdown", dataIndex: "week", key: "week" },
  { title: "Month Breakdown", dataIndex: "month", key: "month" },
  { title: "Bearish OB Zone (1m)", dataIndex: "ob1m", key: "ob1m" },
  { title: "OB Detection Candle (1m)", dataIndex: "obCandle1m", key: "obCandle1m" },
  { title: "Bearish OB Zone (5m)", dataIndex: "ob5m", key: "ob5m" },
  { title: "OB Detection Candle (5m)", dataIndex: "obCandle5m", key: "obCandle5m" },
  { title: "Detected At", dataIndex: "detectedAt", key: "detectedAt" },
];

const breakoutData: TableData[] = [
  {
    key: "1",
    symbol: "HDFCLIFE",
    ltp: "787.85",
    cumulativeVol: "1615802",
    time: "2025-08-14 10:42:00",
    week: "2025-08-14 10:42:15",
    month: "2025-08-14 10:42:15",
    ob1m: "None",
    obCandle1m: "None",
    ob5m: "None",
    obCandle5m: "None",
    detectedAt: "2025-08-14 10:46:16",
  },
];

const breakdownData: TableData[] = [
  {
    key: "1",
    symbol: "BPCL",
    ltp: "320.10",
    cumulativeVol: "6654180",
    time: "2025-08-14 09:35",
    week: "-",
    month: "-",
    ob1m: "None",
    obCandle1m: "None",
    ob5m: "None",
    obCandle5m: "None",
    detectedAt: "2025-08-14 09:35",
  },
];

const Screener: React.FC = () => {
  const [interval, setIntervalValue] = useState(60);
  const [remaining, setRemaining] = useState(60);
  const screens = useBreakpoint();

  useEffect(() => {
    setRemaining(interval); 

    const timer = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          console.log("🔄 Auto-refresh triggered!");
          return interval; 
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [interval]);

  const percent = Math.round(((interval - remaining) / interval) * 100);

  return (
    <div style={{ padding: screens.xs ? 12 : 24, background: "white", minHeight: "100vh" }}>
      <Title level={2} style={{ color: "#0d0d0d" }}>
        🚀 Real-time F&O Breakout Monitor{" "}
        <span style={{ fontWeight: "normal" }}>(with Debugging)</span>
      </Title>

      <Row align="middle" style={{ marginBottom: 12 }}>
        <Col flex="none">
          <ClockCircleOutlined style={{ marginRight: 6, color: "lightblue" }} />
        </Col>
        <Col flex="auto">
          <Text style={{ color: "#0d0d0d" }}>Refresh Interval (seconds)</Text>
        </Col>
      </Row>

      <Slider
        min={30}
        max={120}
        value={interval}
        onChange={(val) => setIntervalValue(val)}
        trackStyle={{ backgroundColor: "red" }}
        handleStyle={{ borderColor: "red", backgroundColor: "white" }}
        railStyle={{ backgroundColor: "#1a1a1a" }}
        tooltip={{ formatter: (val) => `${val}` }}
      />

      <div style={{ marginTop: 20 }}>
        <Progress percent={percent} status="active" />
        <Text type="secondary">
          Refreshing in {remaining} sec (every {interval} sec)
        </Text>
      </div>

      <Space direction="vertical" style={{ marginTop: 20, width: "100%" }}>
        <Button
          size="middle"
          icon={<RocketOutlined style={{ color: "red" }} />}
          style={{ backgroundColor: "white", borderColor: "black", color: "black" }}
          onClick={() => console.log("Monitoring started")}
        >
          Start Monitoring
        </Button>
        
        <Button
          size="middle"
          icon={<StopOutlined style={{ color: "red" }} />}
          style={{ backgroundColor: "white", borderColor: "black", color: "black" }}
          onClick={() => console.log("Monitoring stopped")}
        >
          Stop Monitoring
        </Button>
        
        <Button
          size="middle"
          icon={<DeleteOutlined style={{ color: "red" }} />}
          style={{ backgroundColor: "white", borderColor: "black", color: "black" }}
          onClick={() => console.log("Historical data cleared")}
        >
          Clear Historical Data
        </Button>
      </Space>
      <Divider />

      <Title level={3} style={{ color: "black" }}>✅ Live Breakout Results</Title>
      <Table<TableData>
        columns={breakoutColumns}
        dataSource={breakoutData}
        pagination={false}
        bordered
        size="small"
        scroll={{ x: "max-content" }}
      />
      <Divider />

      <Title level={3} style={{ color: "black" }}>✅ Live Breakdown Results</Title>
      <Table<TableData>
        columns={breakdownColumns}
        dataSource={breakdownData}
        pagination={false}
        bordered
        size="small"
        scroll={{ x: "max-content" }}
      />
    </div>
  );
};

export default Screener;

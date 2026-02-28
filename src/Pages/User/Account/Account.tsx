import React from "react";
import { Tabs } from "antd";
import type { TabsProps } from "antd";
import {
  FileTextOutlined,
  WalletOutlined,
  CreditCardOutlined,
  BookOutlined,
  IdcardOutlined,
  HistoryOutlined,
} from "@ant-design/icons";

import Plan from "./Plan";
import Balance from "./Balance";
import Payment from "./Payment";
import Ledger from "./Ledger";
import License from "./License";
import History from "./History";

const items: TabsProps["items"] = [
  {
    key: "plan",
    label: (
      <>
        <FileTextOutlined /> <span style={{ marginLeft: 6 }}>Plan</span>
      </>
    ),
    children: <Plan />,
  },
  {
    key: "balance",
    label: (
      <>
        <WalletOutlined /> <span style={{ marginLeft: 6 }}>Balance</span>
      </>
    ),
    children: <Balance />,
  },
  {
    key: "payment",
    label: (
      <>
        <CreditCardOutlined /> <span style={{ marginLeft: 6 }}>Payment</span>
      </>
    ),
    children: <Payment />,
  },
  {
    key: "ledger",
    label: (
      <>
        <BookOutlined /> <span style={{ marginLeft: 6 }}>Ledger</span>
      </>
    ),
    children: <Ledger />,
  },
  {
    key: "license",
    label: (
      <>
        <IdcardOutlined /> <span style={{ marginLeft: 6 }}>License</span>
      </>
    ),
    children: <License />,
  },
  {
    key: "history",
    label: (
      <>
        <HistoryOutlined /> <span style={{ marginLeft: 6 }}>History</span>
      </>
    ),
    children: <History />,
  },
];

const Account: React.FC = () => {
  return <Tabs defaultActiveKey="plan" items={items} />;
};

export default Account;

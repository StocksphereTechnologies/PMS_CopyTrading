import React, { useEffect } from "react";
import { Table, Input, Button, Tag } from "antd";
import {
  SearchOutlined,
  PlusOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from "@ant-design/icons";
import { useAccountStore } from "../../../store/accountStore";
import { accountService } from "../../../Services/accountService";

interface TableData {
  key: number;
  account_id: number;
  pseudoAcc: string;
  tradingAcc: string;
  broker: string;
  live: string;
}

interface Props {
  onAddAccount: (account: TableData) => void;
}

const AvailablePseudoAccountsTable: React.FC<Props> = ({ onAddAccount }) => {
  const { accounts, setAccounts } = useAccountStore();

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await accountService.getAll();
      setAccounts(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error("Failed to fetch accounts", error);
    }
  };

  const handleAdd = (account: TableData) => {
    onAddAccount(account);
  };

  const columns = [
    {
      title: "Add",
      key: "add",
      render: (_: any, record: TableData) => (
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="small"
          onClick={() => handleAdd(record)}
        >
          Add
        </Button>
      ),
    },
    {
      title: "Pseudo Acc",
      dataIndex: "pseudoAcc",
      sorter: (a: TableData, b: TableData) =>
        a.pseudoAcc.localeCompare(b.pseudoAcc),
    },
    {
      title: "Trading Acc",
      dataIndex: "tradingAcc",
    },
    {
      title: "Broker",
      dataIndex: "broker",
    },
    {
      title: "Live",
      dataIndex: "live",
      render: (live: string) => (
        <Tag color={live === "Yes" ? "green" : "orange"}>
          {live === "Yes" ? <CheckCircleOutlined /> : <CloseCircleOutlined />}{" "}
          {live}
        </Tag>
      ),
    },
  ];

  const tableData: TableData[] = accounts.map((account: any) => ({
    key: account.account_id,
    account_id: account.account_id,
    pseudoAcc: account.nickname || "N/A",
    tradingAcc: account.trading_login_id,
    broker: account.broker_name,
    live: account.is_enabled ? "Yes" : "No",
  }));

  return (
    <>
      <div style={{ textAlign: "right", marginBottom: 8 }}>
        <Input
          prefix={<SearchOutlined />}
          placeholder="Search"
          style={{ width: 220 }}
        />
      </div>

      <Table
        bordered
        pagination={{ pageSize: 10 }}
        columns={columns}
        dataSource={tableData}
        locale={{ emptyText: "No accounts available" }}
      />

      <p style={{ marginTop: 8 }}>Showing {tableData.length} entries</p>
    </>
  );
};

export default AvailablePseudoAccountsTable;
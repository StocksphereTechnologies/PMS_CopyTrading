import React, { useState, useEffect } from "react";
import { Input, Row, Col, Button, InputNumber, message } from "antd";
import AvailableAccountsTable from "./AvailableAccountsTable";
import { useNavigate, useParams } from "react-router-dom";
import { groupService } from "../../../Services/groupService";
import { useAccountStore } from "../../../store/accountStore";
import GroupAccountsTable from "./GroupAccountsTable";
import Swal from "sweetalert2";

interface TableData {
  key: number;
  account_id: number;
  nickname: string;
  tradingAcc: string;
  broker: string;
  live: string;
}

const CreateGroupAccount: React.FC = () => {

  const [groupAccounts, setGroupAccounts] = useState<TableData[]>([]);
  const [groupName, setGroupName] = useState("");
  const [multiplier, setMultiplier] = useState<number>(1);
  const [description, setDescription] = useState("");
  const { accounts, setAccounts } = useAccountStore();

  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  // Load group when editing
  useEffect(() => {

    if (!id) return;

    const loadGroup = async () => {

      try {

        const data = await groupService.getById(Number(id));
        console.log("Group API response:", data);

        setGroupName(data.name || "");
        setMultiplier(data.multiplier || 1);
        setDescription(data.description || "");

        // backend gives account_ids
        if (data.account_ids && accounts.length > 0) {
          const formattedAccounts = accounts
            .filter((acc: any) => data.account_ids.includes(acc.account_id))
            .map((acc: any, index: number) => ({
              key: index,
              account_id: acc.account_id,
              nickname: acc.nickname,
              tradingAcc: acc.trading_login_id,
              broker: acc.broker_name,
              live: acc.is_enabled ? "Yes" : "No"
            }));
          setGroupAccounts(formattedAccounts);
        }
      } catch (error) {
        console.error("Group Load Error:", error);
      }
    };
    loadGroup();
  }, [id, accounts]);

  const handleAddAccount = (account: TableData) => {

    const exists = groupAccounts.find(
      (a) => a.account_id === account.account_id
    );

    if (!exists) {
      setGroupAccounts([...groupAccounts, account]);
    }
  };

  const handleRemoveAccount = (accountId: number) => {
    const removedAccount = groupAccounts.find(
      (a) => a.account_id === accountId
    );
    // remove from group table
    setGroupAccounts(
      groupAccounts.filter((a) => a.account_id !== accountId)
    );
  };

  const handleSaveGroup = async () => {

    if (!groupName) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Please enter group name"
      });
      return;
    }

    if (groupAccounts.length === 0) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Please add at least one account"
      });
      return;
    }

    try {

      const payload = {
        name: groupName,
        multiplier,
        description,
        account_ids: groupAccounts.map((acc) => acc.account_id)
      };

      if (id) {
        await groupService.update(Number(id), payload);
        await Swal.fire({
          icon: "success",
          title: "Success",
          text: "Account Updated successfully.",
          confirmButtonText: "OK"
        });

      } else {

        await groupService.create(payload);

        await Swal.fire({
          icon: "success",
          title: "Success",
          text: "Account saved successfully.",
          confirmButtonText: "OK"
        });

      }

      navigate("/settings/groupaccounts");

    } catch (error: any) {

      Swal.fire({
        icon: "error",
        title: "Error",
        text: error.response?.data?.detail || "Something went wrong",
        footer: "👉 Help me on this Error! 👈"
      });
    }
  };

  const handleDeleteGroup = async () => {

    if (!id) return;

    const result = await Swal.fire({
      icon: "warning",
      title: "Are you sure?",
      text: "This Group Account will be deleted!",
      showCancelButton: true,
      confirmButtonText: "Yes, delete it!",
      cancelButtonText: "Cancel",
      confirmButtonColor: "#d33"
    });

    if (!result.isConfirmed) return;
    try {
      await groupService.delete(Number(id));

      await Swal.fire({
        icon: "success",
        title: "Success",
        text: "Group account successfully deleted!",
        confirmButtonText: "OK"
      });

      navigate("/settings/groupaccounts");

    } catch (error) {

      Swal.fire({
        icon: "error",
        title: "Error",
        text: "Failed to delete group"
      });
    }
  };

  const availableAccounts = accounts.filter(
    (acc: any) =>
      !groupAccounts.some((g) => g.account_id === acc.account_id)
  );

  return (

    <div style={{ padding: 16 }}>

      <h2 style={{ color: "#0bb", marginBottom: 16 }}>
        {id ? "Edit Group Account" : "Create Group Account"}
      </h2>

      <div
        style={{
          border: "1px solid #d9d9d9",
          borderRadius: 4,
          padding: 20,
          marginBottom: 24
        }}
      >

        <Row gutter={16}>

          <Col span={6}>
            <label>Name</label>
            <Input
              placeholder="Group Name"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
            />
          </Col>

          <Col span={6}>
            <label>
              Qty. Multiplier
              <span style={{ color: "#1890ff" }}>
                {" "} [0.05 to 10000]
              </span>
            </label>

            <InputNumber
              min={0.05}
              max={10000}
              step={0.01}
              value={multiplier}
              onChange={(v) => setMultiplier(Number(v))}
              style={{ width: "100%" }}
            />
          </Col>

          <Col span={12}>
            <label>Description</label>
            <Input
              placeholder="What is this group for?"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Col>
        </Row>

      </div>

      <h3 style={{ color: "#fa8c16" }}>
        Group's Accounts
      </h3>

      <GroupAccountsTable
        accounts={groupAccounts}
        onRemoveAccount={handleRemoveAccount}
      />

      <h3 style={{ color: "#52c41a", marginTop: 24 }}>
        Available Accounts
      </h3>

      <AvailableAccountsTable
        onAddAccount={handleAddAccount}
        selectedAccountIds={groupAccounts.map((acc) => acc.account_id)}
      />

      <Row gutter={12} style={{ marginTop: 16 }}>

        <Col>
          <Button
            onClick={handleSaveGroup}
            style={{
              background: "#0bb",
              color: "#fff"
            }}
          >
            {id ? "Update Group" : "Save"}
          </Button>
        </Col>

        {id && (
          <Col>
            <Button
              danger
              onClick={handleDeleteGroup}
            >
              Delete
            </Button>
          </Col>
        )}
      </Row>
    </div>
  );
};
export default CreateGroupAccount;


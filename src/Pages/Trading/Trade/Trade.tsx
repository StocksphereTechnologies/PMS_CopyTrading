import React, { useEffect, useState } from 'react';
import {
  Form,
  Radio,
  Select,
  Input,
  InputNumber,
  Tooltip,
  Checkbox,
  Switch,
  Button,
  Space,
  Row,
  Col,
  Divider,
  Modal,
  Table,
} from 'antd';
import { useWatch } from 'antd/es/form/Form';
import { InfoCircleOutlined, FileTextOutlined } from '@ant-design/icons';
import tradeService from '../../../Services/tradeService';
import { accountService, Account } from '../../../Services/accountService';
import { notification } from 'antd';
import { groupService } from '../../../Services/groupService';
import Swal from "sweetalert2";
import { useLocation } from "react-router-dom";

const { Option } = Select;

const Trade: React.FC = () => {
  const [form] = Form.useForm();
  const side = useWatch('side', form);
  const orderType = useWatch('orderType', form);
  const product = useWatch('product', form);
  const priceType = useWatch('priceType', form);
  const splitType = useWatch('split', form);

  const [selectedAccountsWithQty, setSelectedAccountsWithQty] = useState<any[]>([]);

  const diffQty = useWatch('diffQty', form);
  const [disablePrice, setDisablePrice] = useState(false);
  const [disableTrigPrice, setDisableTrigPrice] = useState(false);
  const [isRecentModalOpen, setIsRecentModalOpen] = useState(false);
  const [recentSymbols, setRecentSymbols] = useState<
    { key: string; symbol: string; exch: string }[]
  >([]);
  const [submitting, setSubmitting] = useState(false);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loadingAccounts, setLoadingAccounts] = useState(false);
  const groupAcc = useWatch('groupAcc', form);
  const [groups, setGroups] = useState<any[]>([]);

  const [resultModalOpen, setResultModalOpen] = useState(false);
  const [tradeResults, setTradeResults] = useState<any[]>([]);
  const [successCount, setSuccessCount] = useState(0);
  const [failureCount, setFailureCount] = useState(0);

  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [diffQtyError, setDiffQtyError] = useState<string>("");

  const location = useLocation();

  useEffect(() => {
    const fetchAccounts = async () => {
      setLoadingAccounts(true);
      try {
        const response = await accountService.getAll(true);
        if (response && response.accounts) {
          setAccounts(response.accounts);
        } else if (Array.isArray(response)) {
          setAccounts(response);
        } else {
          setAccounts([]);
        }
      } catch (error) {
        console.error('Failed to fetch accounts:', error);
      } finally {
        setLoadingAccounts(false);
      }
    };
    fetchAccounts();
  }, []);

  useEffect(() => {
    fetchGroups();
  }, []);

  useEffect(() => {
    if (location.state) {
      form.setFieldsValue({
        symbol: location.state.symbol,
        exchange: location.state.exchange,
        side: location.state.side,
        price: location.state.price,
        quantity: location.state.quantity,
        scrip_code: location.state.scrip_code,
      });
    }
  }, [location.state]);

  const fetchGroups = async () => {
    try {
      const res = await groupService.getAll();
      setGroups(res);
    } catch (error) {
      console.error("Failed to fetch groups");
    }
  };

  const handleSubmit = async (values: any) => {
    setSubmitting(true);
    try {
      const cleanNumber = (val: any) => {
        const num = Number(val);
        return (isNaN(num) || num === 0) ? undefined : num;
      };

      let selectedAccounts = values.account_ids;

      if (values.groupAcc) {

        const group = groups.find(
          (g: any) => g.id === values.account_ids?.[0]
        );

      }

      if (values.diffQty) {
        const isEmptySelection =
          !selectedAccountsWithQty || selectedAccountsWithQty.length === 0;

        if (isEmptySelection) {

          const message = values.groupAcc
            ? "Quantity calculation failed: No groups selected"
            : "Quantity calculation failed: No accounts selected";

          setDiffQtyError(message);

          await Swal.fire({
            icon: "error",
            title: "Error",
            text: message,
            confirmButtonText: "OK"
          });

          setSubmitting(false);
          return;
        }
      }

      const requestData = {
        symbol: values.symbol,
        exchange: values.exchange,
        scrip_code: values.scrip_code,
        side: values.side,
        quantity: Number(values.quantity),
        order_type: values.priceType === 'MARKET' ? 'MARKET' : (values.priceType === 'LIMIT' ? 'LIMIT' : (values.priceType === 'STOP_LOSS' ? 'SL' : 'SL_M')),
        price: values.priceType !== 'MARKET' && values.priceType !== 'SL_MARKET' ? cleanNumber(values.price) : undefined,
        trigger_price: values.priceType === 'STOP_LOSS' || values.priceType === 'SL_MARKET' ? cleanNumber(values.triggerPrice) : undefined,
        product: values.product,
        disclosed_quantity: cleanNumber(values.disclosedQty),
        account_ids: values.diffQty ? undefined : selectedAccounts,
        accounts_with_qty: values.diffQty
          ? selectedAccountsWithQty.map((item) => ({
            ...(groupAcc
              ? { group_id: item.id }
              : { account_id: item.account_id }),
            quantity: item.quantity || 1,
          }))
          : undefined,
        Target: cleanNumber(values.Target),
        Stoploss: cleanNumber(values.Stoploss),
        trailing_stoploss: cleanNumber(values['Trail. Stoploss']),
        variety: (values.orderType || 'REGULAR').toLowerCase(),
        validity: values.timeInForce || 'DAY',
        amo: !!values.amo,
        groupAcc: !!values.groupAcc,
        diffQty: !!values.diffQty,
        multiplier: !!values.multiplier,
        split: values.split || 'NO',
        splitQty: cleanNumber(values.splitQty)
      };

      const result = await tradeService.placeTrade(requestData as any);

      const executions = result.details || [];

      const success = executions.filter((e: any) => e.status === "SUCCESS").length;
      const failure = executions.filter((e: any) => e.status !== "SUCCESS").length;

      setSuccessCount(success);
      setFailureCount(failure);

      const rows = executions.map((e: any, index: number) => ({
        key: index,
        account:
          accounts.find(a => a.account_id === e.account_id)?.nickname ||
          e.account_id,
        orderId: e.status === "SUCCESS" ? e.order_id : e.error_reason,
        status: e.status
      }));

      setTradeResults(rows);
      setResultModalOpen(true);

      form.resetFields(['symbol', 'quantity', 'price', 'triggerPrice']);
    } catch (error: any) {
      notification.error({
        message: 'Trade Failed',
        description: error.response?.data?.detail || error.message || 'An error occurred while placing the trade.',
        placement: 'topRight'
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    form.resetFields();
  };

  useEffect(() => {
    if (!diffQty) {
      setSelectedAccountsWithQty([]);
      setSelectedRowKeys([]);
      setDiffQtyError("");
    }
  }, [diffQty, groupAcc]);

  useEffect(() => {
    let priceDisabled = false;
    let trigDisabled = false;

    if (orderType === 'BO' && product === 'INTRADAY') {
      switch (priceType) {
        case 'LIMIT':
          trigDisabled = true;
          priceDisabled = false;
          break;
        case 'MARKET':
          trigDisabled = true;
          priceDisabled = true;
          break;
        case 'STOP_LOSS':
          trigDisabled = false;
          priceDisabled = false;
          break;
        case 'SL_MARKET':
          trigDisabled = false;
          priceDisabled = true;
          break;
        default:
          break;
      }
    } else if (orderType === 'REGULAR') {
      switch (priceType) {
        case 'LIMIT':
          trigDisabled = true;
          priceDisabled = false;
          break;
        case 'MARKET':
          trigDisabled = true;
          priceDisabled = true;
          break;
        case 'STOP_LOSS':
          trigDisabled = false;
          priceDisabled = false;
          break;
        case 'SL_MARKET':
          trigDisabled = false;
          priceDisabled = true;
          break;
        default:
          break;
      }
    } else if (orderType === 'CO') {
      switch (priceType) {
        case 'LIMIT':
          trigDisabled = false;
          priceDisabled = false;
          break;
        case 'MARKET':
          trigDisabled = false;
          priceDisabled = true;
          break;
        default:
          break;
      }
    }

    setDisablePrice(priceDisabled);
    setDisableTrigPrice(trigDisabled);
  }, [orderType, product, priceType]);

  const recentCols = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
      sorter: (a: any, b: any) => a.symbol.localeCompare(b.symbol),
    },
    {
      title: 'Exch',
      dataIndex: 'exch',
      key: 'exch',
      sorter: (a: any, b: any) => a.exch.localeCompare(b.exch),
    },
  ];

  const resultColumns = [
    {
      title: "Account",
      dataIndex: "account"
    },
    {
      title: "Order ID",
      dataIndex: "orderId",
      render: (text: any, record: any) => (
        <span style={{
          color: record.status === "FAILED" ? "red" : "black"
        }}>
          {text}
        </span>
      )
    },
    {
      title: "Help",
      render: (_: any, record: any) =>
        record.status === "FAILED" ? (
          <a>Help Me</a>
        ) : null
    }
  ];
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        background: '#f0f2f5',
        padding: '20px 0',
        minHeight: '50vh',
      }}
    >
      <div
        style={{
          background: side === 'SELL' ? '#fff1f0' : '#f6ffed',
          padding: 16,
          borderRadius: 10,
          width: 1000,
          border: side === 'SELL' ? '2px solid #ffa39e' : '2px solid #80EF80',
          boxShadow:
            side === 'SELL'
              ? '0 0 12px 4px #ffa39e'
              : '0 0 12px 4px #80EF80',
          transition: 'all 0.3s ease-in-out',
        }}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            side: 'BUY',
            orderType: 'REGULAR',
            product: 'INTRADAY',
            priceType: 'LIMIT',
            exchange: 'NSE',
            quantity: 1,
            price: undefined,
            triggerPrice: undefined,
            disclosedQty: undefined,
            timeInForce: 'DAY',
            split: 'NO',
            amo: false,
            groupAcc: false,
            multiplier: false
          }}
          onFinish={handleSubmit}
        >
          <Row gutter={[12, 8]}>
            {/* BUY / SELL */}
            <Col span={24}>
              <Form.Item name="side" style={{ marginBottom: 0 }}>
                <Radio.Group size="small">
                  <Radio value="BUY">BUY</Radio>
                  <Radio value="SELL">SELL</Radio>
                </Radio.Group>
              </Form.Item>
            </Col>

            {/* Order Type */}
            <Col span={6}>
              <Form.Item name="orderType" style={{ marginBottom: 0 }}>
                <Radio.Group size="small">
                  <Tooltip title="Regular Order">
                    <Radio value="REGULAR">REGULAR</Radio>
                  </Tooltip>
                  <Tooltip title="Bracket Order">
                    <Radio value="BO">BO</Radio>
                  </Tooltip>
                  <Tooltip title="Cover Order">
                    <Radio value="CO">CO</Radio>
                  </Tooltip>
                </Radio.Group>
              </Form.Item>
            </Col>

            {/* File icon opens Recent Symbols modal */}
            <Col span={2}>
              <Button
                icon={<FileTextOutlined style={{ fontSize: '32px', color: '#1890ff' }} />}
                size="large"
                type="text"
                onClick={() => {
                  setIsRecentModalOpen(true);
                }}
              />
            </Col>

            {/* Exchange */}
            <Col span={4}>
              <Form.Item name="exchange" style={{ marginBottom: 0 }}>
                <Select size="large">
                  <Option value="NSE">NSE</Option>
                  <Option value="BSE">BSE</Option>
                  <Option value="MCX">MCX</Option>
                  <Option value="NFO">NFO</Option>
                </Select>
              </Form.Item>
            </Col>

            {/* Symbol */}
            <Col span={12}>
              <Form.Item
                name="symbol"
                rules={[{ required: true, message: 'Enter symbol' }]}
                style={{ marginBottom: 0 }}
              >
                <Input
                  size="large"
                  placeholder="Symbol"
                  suffix={
                    <Tooltip title="Search using instrument symbol...(use words like 'future','call','put' or enter strike price for options">
                      <InfoCircleOutlined />
                    </Tooltip>
                  }
                />
              </Form.Item>
            </Col>

            {/* Product */}
            <Col span={12}>
              <Form.Item name="product" style={{ marginBottom: 0 }}>
                <Radio.Group size="small">
                  <Radio value="INTRADAY">INTRADAY</Radio>
                  <Tooltip title="Delivery position in STOCKS">
                    <Radio value="DELIVERY" disabled={orderType === 'CO' || orderType === 'BO'}>
                      DELIVERY
                    </Radio>
                  </Tooltip>
                  <Tooltip title="Carry forward positions in DERIVATIVES">
                    <Radio value="NORMAL" disabled={orderType === 'CO' || orderType === 'BO'}>
                      NORMAL
                    </Radio>
                  </Tooltip>
                  <Tooltip title="Margin Trading Facility(MTF)">
                    <Radio value="MTF" disabled={orderType === 'CO' || orderType === 'BO'}>
                      MTF
                    </Radio>
                  </Tooltip>
                </Radio.Group>
              </Form.Item>
            </Col>

            {/* Price Type */}
            <Col span={12}>
              <Form.Item name="priceType" style={{ marginBottom: 0 }}>
                <Radio.Group size="small">
                  <Radio value="LIMIT">LIMIT</Radio>
                  <Radio value="MARKET">MARKET</Radio>
                  <Radio value="STOP_LOSS" disabled={orderType === 'CO'}>
                    STOP_LOSS
                  </Radio>
                  <Radio value="SL_MARKET" disabled={orderType === 'CO'}>
                    SL_MARKET
                  </Radio>
                </Radio.Group>
              </Form.Item>
            </Col>

            {/* Qty */}
            <Col span={4}>
              <Form.Item label="Qty" name="quantity">
                <InputNumber
                  size="large"
                  min={1}
                  controls={false}
                  style={{ width: '100%' }}
                  addonBefore={
                    <Button
                      size="small"
                      onClick={() => {
                        const current = form.getFieldValue('quantity') || 1;
                        form.setFieldsValue({ quantity: Math.max(1, current - 1) });
                      }}
                    >
                      −
                    </Button>
                  }
                  addonAfter={
                    <Button
                      size="small"
                      onClick={() => {
                        const current = form.getFieldValue('quantity') || 1;
                        form.setFieldsValue({ quantity: current + 1 });
                      }}
                    >
                      +
                    </Button>
                  }
                />
              </Form.Item>
            </Col>

            {/* Price */}
            <Col span={4}>
              <Form.Item label="Price" name="price">
                <Input size="large" prefix="₹" disabled={disablePrice} />
              </Form.Item>
            </Col>

            {/* Trigger Price */}
            <Col span={4}>
              <Form.Item label="Trig. Price" name="triggerPrice">
                <Input size="large" prefix="₹" disabled={disableTrigPrice} />
              </Form.Item>
            </Col>

            {/* Disclosed Qty */}
            <Col span={4}>
              <Form.Item label="Disclosed Qty." name="disclosedQty">
                <InputNumber size="large" min={0} style={{ width: '100%' }} />
              </Form.Item>
            </Col>

            {/* Accounts & Group's */}

            {!diffQty && (
              <Col span={8}>
                <Form.Item
                  label={groupAcc ? "Groups" : "Accounts"}
                  name="account_ids"
                  rules={[{ required: true, message: "Select at least one account" }]}
                >
                  <Select
                    mode="multiple"
                    size="large"
                    placeholder={groupAcc ? "Select Groups" : "Select Accounts"}
                  >
                    {groupAcc &&
                      groups.map((grp: any) => (
                        <Option key={grp.id} value={grp.id}>
                          {grp.name} ({grp.totalAccounts} Accounts)
                        </Option>
                      ))}

                    {!groupAcc &&
                      accounts.map((acc: any) => (
                        <Option key={acc.account_id} value={acc.account_id}>
                          {acc.nickname || acc.account_name || acc.trading_login_id}
                        </Option>
                      ))}
                  </Select>
                </Form.Item>
              </Col>
            )}

            {/* BO Fields */}
            {orderType === 'BO' && (
              <>
                <Col span={4}>
                  <Form.Item label="Target" name="Target">
                    <InputNumber size="large" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item label="Stoploss" name="Stoploss">
                    <InputNumber size="large" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={4}>
                  <Form.Item label="Trail. Stoploss" name="Trail. Stoploss">
                    <InputNumber size="large" min={0} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </>
            )}

            {/* Time in Force + AMO */}
            <Col span={12}>
              <Space>
                <Form.Item name="timeInForce" style={{ marginBottom: 0 }}>
                  <Radio.Group size="small">
                    <Radio value="DAY" disabled={orderType === 'CO' || orderType === 'BO'}>
                      DAY
                    </Radio>
                    <Radio value="IOC" disabled={orderType === 'CO' || orderType === 'BO'}>
                      IOC
                    </Radio>
                  </Radio.Group>
                </Form.Item>
                <Form.Item name="amo" valuePropName="checked" style={{ marginBottom: 0 }}>
                  <Checkbox>AMO</Checkbox>
                </Form.Item>
              </Space>
            </Col>

            {/* Switches */}

            <Col span={4}>
              <Form.Item label="Group Acc" name="groupAcc" valuePropName="checked">
                <Switch style={{ transform: 'scale(1.5)' }} />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item label="Diff. Qty." name="diffQty" valuePropName="checked">
                <Switch style={{ transform: 'scale(1.5)' }} />
              </Form.Item>
            </Col>
            <Col span={4}>
              <Form.Item label="Multiplier" name="multiplier" valuePropName="checked">
                <Switch style={{ transform: 'scale(1.5)' }} />
              </Form.Item>
            </Col>

            {/* Split Order */}
            <Col span={24}>
              <Form.Item label="Split Order" name="split">
                <Radio.Group size="small">
                  <Tooltip title="Do not split the order">
                    <Radio value="NO">NO</Radio>
                  </Tooltip>
                  <Tooltip title="Split order using quantity freeze limit">
                    <Radio value="AUTO">AUTO</Radio>
                  </Tooltip>
                  <Tooltip title="Split order as per quantity specified by order">
                    <Radio value="QTY">QTY</Radio>
                  </Tooltip>
                </Radio.Group>
              </Form.Item>
              {['REGULAR', 'BO', 'CO'].includes(orderType) && splitType === 'QTY' && (
                <Form.Item label="Split Qty." name="splitQty" style={{ marginTop: 8 }}>
                  <InputNumber size="large" min={0} style={{ width: 200 }} />
                </Form.Item>
              )}
            </Col>

            {/* Diff Qty Table */}
            {diffQty && (
              <Col span={24}>
                <Table
                  rowKey={groupAcc ? "id" : "account_id"}
                  dataSource={groupAcc ? groups : accounts}
                  loading={loadingAccounts}
                  pagination={false}
                  rowSelection={{
                    selectedRowKeys,
                    onChange: (keys, rows) => {
                      setSelectedRowKeys(keys);

                      setSelectedAccountsWithQty(
                        rows.map((r: any) => ({
                          quantity: 1,
                          ...(groupAcc
                            ? { id: r.id }               // ✅ group
                            : { account_id: r.account_id }) // ✅ account
                        }))
                      );
                    },
                  }}
                  columns={[
                    {
                      title: "Account",
                      dataIndex: "nickname",
                      render: (_: any, record: any) =>
                        groupAcc
                          ? record.name
                          : record.nickname || record.account_name || record.trading_login_id,
                    },
                    {
                      title: "Quantity",
                      render: (_: any, record: any) => (
                        <InputNumber
                          min={1}
                          value={
                            selectedAccountsWithQty.find((item) =>
                              groupAcc
                                ? item.id === record.id
                                : item.account_id === record.account_id
                            )?.quantity || 1
                          }
                          onChange={(val) => {
                            setSelectedAccountsWithQty((prev) =>
                              prev.map((item) =>
                                groupAcc
                                  ? item.id === record.id
                                  : item.account_id === record.account_id
                                    ? { ...item, quantity: val }
                                    : item
                              )
                            );
                          }}
                        />
                      ),
                    },
                  ]}
                />
              </Col>
            )}

            {/* Buttons */}
            <Col span={24}>
              <Divider style={{ margin: '8px 0' }} />
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    size="small"
                    danger={side === 'SELL'}
                    loading={submitting}
                  >
                    {side === 'SELL' ? 'SELL' : 'BUY'}
                  </Button>
                  <Button htmlType="button" onClick={handleReset} size="small">
                    Reset
                  </Button>
                </Space>
              </div>
            </Col>
          </Row>
        </Form>
      </div>

      <Modal
        open={resultModalOpen}
        footer={[
          <Button
            key="ok"
            type="primary"
            onClick={() => setResultModalOpen(false)}
          >
            OK
          </Button>
        ]}
        onCancel={() => setResultModalOpen(false)}
        width={600}
        centered
      >

        <h2 style={{ textAlign: "center" }}>
          <span style={{ color: "#07b08a" }}>
            Success: {successCount}
          </span>
          {" - "}
          <span style={{ color: "red" }}>
            Failure: {failureCount}
          </span>
        </h2>

        <Table
          columns={resultColumns}
          dataSource={tradeResults}
          pagination={false}
        />

      </Modal>

    </div>
  );
};

export default Trade;
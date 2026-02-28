import React, { useState, useEffect } from "react";
import { Input, Button, Checkbox, Row, Col, Card, Select, Tooltip, message } from "antd";
import { EyeOutlined, CheckOutlined, SaveOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { accountService, ZerodhaAccountData, FivePaisaAccountData } from "../../../Services/accountService";
import { useAccountStore } from "../../../store/accountStore";

const labelStyle: React.CSSProperties = {
  fontWeight: 600,
  color: "#555",
  marginBottom: 4,
};

const tradingPlatformMap: Record<string, string[]> = {
  "5Paisa": ["FP_API_TOTP", "XTS_FIVE_PAISA"],
  "AC Agarwal": ["XTS_AGARWAL"],
  "AETRAM": ["XTS_AETRAM", "XTS_AETRAM_IPV6"],
  "AliceBlue": ["ALICE_API", "ALICE_API_IPV6"],
  "Ambalal": ["XTS_AMBALAL"],
  "AnandRathi": ["XTS_A_RATHI_IPV6", "XTS_ANAND_RATHI"],
  "Angel": ["SMART_API_IPV6", "SMART_API", "SMART_API_M"],
  "ARHAM": ["XTS_ARHAM"],
  "ATS": ["XTS_ATS"],
  "Axis": ["XTS_AXIS"],
  "Choice": ["CHOICE_API", "CHOICE_API_TOTP", "CHOICE_API_IPV6"],
  "DBOnline": ["XTS_DEONLINE"],
  "Dhan": ["DHAN_V2_AT_IPV6", "DHAN_V2_IPV6", "DHAN_V2"],
  "Eureka": ["XTS_EUREKA"],
  "Eureka - PROP": ["XTS_EUREKA_PROP_IPV6", "XTS_EUREKA_PROP"],
  "Finvasia": ["SHOONYA_BETA", "KAMBALA_FINVASIA"],
  "Flattrade": ["KAMBALA_FLATTRADE"],
  "Fyers": ["FYERS_API_IPV6", "FYERS_API"],
  "IIFL": ["IIFL_MKT_API_IPV6", "IIFL_API", "XTS_IIFL"],
  "Jainam": ["XTS_JAINAM", "XTS_JAINAM_IPV6"],
  "Jainam - PROP": [
    "XTS_JAINAM_PROP_A",
    "XTS_JAINAM_PROP_B",
    "XTS_JAINAM_PROP_C",
    "XTS_JAINAM_PROP_D",
  ],
  "Kotak": ["KOTAK_NEO", "KOTAK_NEO_TOTP"],
  "Mastertrust": ["MASTERTRUST"],
  "MLB": ["XTS_MLB"],
  "Motilal": ["MOTILAL_API", "MOTILAL_API_IPV6", "XTS_MOTILAL"],
  "Nuvama": ["NUVAMA_RETAIL"],
  "PESB": ["XTS_PESB"],
  "Prabhudas Lilladher": ["KAMBALA_PLINDIA"],
  "Profitmart": ["KAMBALA_PROFITMART"],
  "Religare": ["XTS_RELIGARE"],
  "Rmoney": ["XTS_RMONEY"],
  "SAS": ["SAS", "SAS_STOCKO_API", "SAS_STOCKO_API_IPV6"],
  "Share India": ["XTS_SHARE_IND"],
  "Share India - PROP": ["XTS_SHARE_IND_PROP", "XTS_SHARE_IND_PROP_M"],
  "SMC": ["XTS_SMC"],
  "SW Capital": ["XTS_SW_CAPITAL", "XTS_SW_CAPITAL_IPV6"],
  "Tradejini": ["KAMBALA_TRADEJINI"],
  "Tradeswift": ["XTS_TSWIFT"],
  "Upstox": ["UPSTOX", "UPSTOX_API", "UPSTOX_API_IPV6"],
  "WisdomCapital": ["XTS_WISDOM"],
  "Zebu": ["MYNT_API", "MYNT_API_IPV6", "XTS_ZEBU"],
  "Zerodha": ["ZERODHA_API_IPV6","ZERODHA_API", "ZERODHA_API_M_IPV6", "ZERODHA_API_M", "KITE_IPV6", "KITE"],
};

const brokerOptions = [
  "5Paisa",
  "AC Agarwal",
  "AETRAM",
  "AliceBlue",
  "Ambalal",
  "AnandRathi",
  "Angel",
  "ARHAM",
  "ATS",
  "Axis",
  "Choice",
  "DBOnline",
  "Dhan",
  "Eureka",
  "Eureka - PROP",
  "Finvasia",
  "Flattrade",
  "Fyers",
  "IIFL",
  "Jainam",
  "Jainam - PROP",
  "Kotak",
  "Mastertrust",
  "MLB",
  "Motilal",
  "Nuvama",
  "PESB",
  "Prabhudas Lilladher",
  "Profitmart",
  "Religare",
  "Rmoney",
  "SAS",
  "Share India",
  "Share India - PROP",
  "SMC",
  "SW Capital",
  "Tradejini",
  "Tradeswift",
  "Upstox",
  "WisdomCapital",
  "Zebu",
  "Zerodha",
];

const CreateTradingAccount: React.FC = () => {
  const navigate = useNavigate();
  const addAccount = useAccountStore((state) => state.addAccount);

  // Broker selection
  const [broker, setBroker] = useState("Zerodha");
  const [platform, setPlatform] = useState<string | undefined>(undefined);

  // Common fields
  const [loginId, setLoginId] = useState("");
  const [totp, setTotp] = useState("");
  const [showTotp, setShowTotp] = useState(false);
  const [nickname, setNickname] = useState("");
  const [useLoginAsNickname, setUseLoginAsNickname] = useState(false);

  // Zerodha specific
  const [zerodhaPassword, setZerodhaPassword] = useState("");
  const [showZerodhaPassword, setShowZerodhaPassword] = useState(false);
  const [zerodhaApiKey, setZerodhaApiKey] = useState("");
  const [showZerodhaApiKey, setShowZerodhaApiKey] = useState(false);
  const [zerodhaApiSecret, setZerodhaApiSecret] = useState("");
  const [showZerodhaApiSecret, setShowZerodhaApiSecret] = useState(false);

  // 5paisa specific
  const [mpin, setMpin] = useState("");
  const [showMpin, setShowMpin] = useState(false);
  const [fivePaisaUserId, setFivePaisaUserId] = useState("");
  const [showFivePaisaUserId, setShowFivePaisaUserId] = useState(false);
  const [fivePaisaLoginPassword, setFivePaisaLoginPassword] = useState("");
  const [showFivePaisaLoginPassword, setShowFivePaisaLoginPassword] = useState(false);
  const [userKey, setUserKey] = useState("");
  const [showUserKey, setShowUserKey] = useState(false);
  const [appSource, setAppSource] = useState("");
  const [fivePaisaAppName, setFivePaisaAppName] = useState("");
  const [fivePaisaEncryptionKey, setFivePaisaEncryptionKey] = useState("");

  // State
  const [validating, setValidating] = useState(false);
  const [isValidated, setIsValidated] = useState(false);
  const [saving, setSaving] = useState(false);

  // Auto-set nickname
  useEffect(() => {
    if (useLoginAsNickname) {
      setNickname(loginId);
    }
  }, [loginId, useLoginAsNickname]);

  // Reset validation when broker changes
  useEffect(() => {
    setIsValidated(false);
  }, [broker]);

  // Set default platform when broker changes
  useEffect(() => {
    const platforms = tradingPlatformMap[broker];
    if (platforms && platforms.length > 0) {
      setPlatform(platforms[0]);
    }
  }, [broker]);

  const handleValidate = async () => {
    // Only Zerodha and 5Paisa are supported
    if (broker !== "Zerodha" && broker !== "5Paisa") {
      message.warning(`${broker} is not yet supported. Only Zerodha and 5Paisa are currently available.`);
      return;
    }

    setValidating(true);
    setIsValidated(false);

    try {
      let accountData: ZerodhaAccountData | FivePaisaAccountData;

      if (broker === "Zerodha") {
        // Validate required fields
        if (!loginId || !zerodhaPassword || !totp || !zerodhaApiKey || !zerodhaApiSecret) {
          message.error("Please fill all required fields for Zerodha");
          return;
        }

        accountData = {
          broker_name: "ZERODHA",
          trading_login_id: loginId,
          trading_password: zerodhaPassword,
          totp_secret_key: totp,
          api_key: zerodhaApiKey,
          api_secret: zerodhaApiSecret,
          nickname: nickname || undefined,
        };
      } else {
        // 5paisa
        // Validate required fields
        if (!loginId || !mpin || !totp || !fivePaisaUserId || !fivePaisaLoginPassword || !userKey || !appSource) {
          message.error("Please fill all required fields for 5paisa");
          return;
        }

        accountData = {
          broker_name: "FIVEPAISA",
          trading_login_id: loginId,
          mpin: mpin,
          totp_secret_key: totp,
          user_id: fivePaisaUserId,
          login_password: fivePaisaLoginPassword,
          user_key: userKey,
          app_source: appSource,
          api_key: fivePaisaAppName || undefined,
          api_secret: fivePaisaEncryptionKey || undefined,
          nickname: nickname || undefined,
        };
      }

      const result = await accountService.validate(accountData);

      if (result.valid) {
        message.success(result.message);
        setIsValidated(true);
      } else {
        message.error(result.message);
        setIsValidated(false);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || "Validation failed";
      message.error(errorMsg);
      setIsValidated(false);
    } finally {
      setValidating(false);
    }
  };

  const handleSave = async () => {
    if (!isValidated) {
      message.warning("Please validate credentials first");
      return;
    }

    setSaving(true);

    try {
      let accountData: ZerodhaAccountData | FivePaisaAccountData;

      if (broker === "Zerodha") {
        accountData = {
          broker_name: "ZERODHA",
          trading_login_id: loginId,
          trading_password: zerodhaPassword,
          totp_secret_key: totp,
          api_key: zerodhaApiKey,
          api_secret: zerodhaApiSecret,
          nickname: nickname || undefined,
          is_enabled: true,
        };
      } else {
        accountData = {
          broker_name: "FIVEPAISA",
          trading_login_id: loginId,
          mpin: mpin,
          totp_secret_key: totp,
          user_id: fivePaisaUserId,
          login_password: fivePaisaLoginPassword,
          user_key: userKey,
          app_source: appSource,
          api_key: fivePaisaAppName || undefined,
          api_secret: fivePaisaEncryptionKey || undefined,
          nickname: nickname || undefined,
          is_enabled: true,
        };
      }

      const newAccount = await accountService.create(accountData);
      addAccount(newAccount);

      message.success("Account created successfully!");
      navigate("/settings/tradingaccounts");
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || "Failed to create account";
      message.error(errorMsg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ color: "#00a6a6", marginBottom: 4 }}>
        Trading Account
      </h1>

      <p style={{ color: "#c45a00", marginBottom: 16 }}>
        Add your trading account details here
      </p>

      {broker === "Zerodha" && (
        <Card 
          size="small" 
          style={{ marginBottom: 24, border: '1px solid #ffe7ba', background: '#fffbe6' }}
          title={<span style={{ color: '#d46b08' }}>Zerodha API Configuration</span>}
        >
          <p style={{ margin: 0 }}>Please configure your Kite Connect app with these URLs:</p>
          <Row gutter={16} style={{ marginTop: 8 }}>
            <Col span={12}>
              <div style={labelStyle}>Redirect URL (HTTP is okay)</div>
              <Input readOnly value="http://127.0.0.1:8000/api/v1/accounts/zerodha/callback" />
            </Col>
            <Col span={12}>
              <div style={labelStyle}>Postback URL (Must be HTTPS)</div>
              <Input readOnly value="https://127.0.0.1:8000/api/v1/accounts/zerodha/postback" />
            </Col>
          </Row>
          <p style={{ marginTop: 12, fontSize: '12px', color: '#8c8c8c' }}>
            * <b>Tip:</b> Zerodha requires HTTPS for Postbacks. For local development, you can use any <code>https://</code> URL (like <code>https://google.com</code>) as a <b>dummy postback</b> to save your app settings. Authentication only relies on the Redirect URL.
          </p>
        </Card>
      )}

      <p style={{ color: "#c45a00", marginBottom: 24 }}>
        Your trading account information is completely secure, more details are
        available in <b>Security Concerns</b>.
      </p>

      <Row justify="center">
        <Col xs={24} sm={22} md={16} lg={12}>
          <Card bordered>

            <label style={{ fontWeight: 600 }}>Stock Broker</label>
            <Select
              value={broker}
              onChange={(value) => setBroker(value)}
              showSearch
              style={{ width: "100%", marginBottom: 16 }}
            >
              {brokerOptions.map((b) => (
                <Select.Option key={b} value={b}>
                  {b}
                </Select.Option>
              ))}
            </Select>

            <Button
              block
              style={{
                background: "#11c26d",
                color: "#fff",
                marginTop: 12,
                marginBottom: 20,
              }}
            >
              Need HELP? Click Here!
            </Button>

            <label style={{ fontWeight: 600 }}>Trading Platform</label>

            <Select
              value={platform}
              onChange={setPlatform}
              placeholder="Select Trading Platform"
              style={{ width: "100%", marginBottom: 16 }}
            >
              {(tradingPlatformMap[broker] || []).map((p) => (
                <Select.Option key={p} value={p}>
                  {p}
                </Select.Option>
              ))}
            </Select>

            <Button
              block
              style={{
                background: "#00a6a6",
                color: "#fff",
                marginTop: 12,
                marginBottom: 20,
              }}
            >
              Get Static IP
            </Button>

            {/* Common Fields */}
            <div style={labelStyle}>Trading Platform Login ID</div>
            <Tooltip
              title={broker === "Zerodha" ? "Zerodha Client ID" : broker === "5Paisa" ? "5paisa Client Code (8-digit)" : "Login ID"}
              placement="right"
              color="#000"
            >
              <Input
                value={loginId}
                onChange={(e) => setLoginId(e.target.value)}
                placeholder={broker === "Zerodha" ? "Client ID" : broker === "5Paisa" ? "Client Code" : "Login ID"}
                suffix={<CheckOutlined />}
                style={{ marginBottom: 16 }}
              />
            </Tooltip>

            <div style={labelStyle}>TOTP Key</div>
            <Input
              type={showTotp ? "text" : "password"}
              value={totp}
              onChange={(e) => setTotp(e.target.value)}
              placeholder="TOTP Secret Key"
              suffix={<EyeOutlined onClick={() => setShowTotp(!showTotp)} style={{ cursor: 'pointer' }} />}
            />
            <Checkbox
              checked={showTotp}
              onChange={(e) => setShowTotp(e.target.checked)}
              style={{ margin: "8px 0 16px" }}
            >
              Show
            </Checkbox>

            {/* Zerodha Specific Fields */}
            {broker === "Zerodha" && (
              <>
                <div style={labelStyle}>Trading Password</div>
                <Input
                  type={showZerodhaPassword ? "text" : "password"}
                  value={zerodhaPassword}
                  onChange={(e) => setZerodhaPassword(e.target.value)}
                  placeholder="Zerodha login password"
                  suffix={<EyeOutlined onClick={() => setShowZerodhaPassword(!showZerodhaPassword)} style={{ cursor: 'pointer' }} />}
                />
                <Checkbox
                  checked={showZerodhaPassword}
                  onChange={(e) => setShowZerodhaPassword(e.target.checked)}
                  style={{ margin: "8px 0 16px" }}
                >
                  Show password
                </Checkbox>

                <div style={labelStyle}>Kite API Key</div>
                <Input
                  type={showZerodhaApiKey ? "text" : "password"}
                  value={zerodhaApiKey}
                  onChange={(e) => setZerodhaApiKey(e.target.value)}
                  placeholder="Kite Connect API Key"
                  suffix={<EyeOutlined onClick={() => setShowZerodhaApiKey(!showZerodhaApiKey)} style={{ cursor: 'pointer' }} />}
                />
                <Checkbox
                  checked={showZerodhaApiKey}
                  onChange={(e) => setShowZerodhaApiKey(e.target.checked)}
                  style={{ margin: "8px 0 16px" }}
                >
                  Show
                </Checkbox>

                <div style={labelStyle}>Kite API Secret</div>
                <Input
                  type={showZerodhaApiSecret ? "text" : "password"}
                  value={zerodhaApiSecret}
                  onChange={(e) => setZerodhaApiSecret(e.target.value)}
                  placeholder="Kite Connect API Secret"
                  suffix={<EyeOutlined onClick={() => setShowZerodhaApiSecret(!showZerodhaApiSecret)} style={{ cursor: 'pointer' }} />}
                />
                <Checkbox
                  checked={showZerodhaApiSecret}
                  onChange={(e) => setShowZerodhaApiSecret(e.target.checked)}
                  style={{ margin: "8px 0 16px" }}
                >
                  Show
                </Checkbox>
              </>
            )}

            {/* 5paisa Specific Fields */}
            {broker === "5Paisa" && (
              <>
                <div style={labelStyle}>MPIN (6-digit)</div>
                <Input
                  type={showMpin ? "text" : "password"}
                  value={mpin}
                  onChange={(e) => setMpin(e.target.value)}
                  placeholder="6-digit MPIN"
                  maxLength={6}
                  suffix={<EyeOutlined onClick={() => setShowMpin(!showMpin)} style={{ cursor: 'pointer' }} />}
                />
                <Checkbox
                  checked={showMpin}
                  onChange={(e) => setShowMpin(e.target.checked)}
                  style={{ margin: "8px 0 16px" }}
                >
                  Show
                </Checkbox>

                <div style={labelStyle}>5paisa USER_ID</div>
                <Tooltip title="Different from Client Code! Get from 5paisa API settings" placement="right" color="#000">
                  <Input
                    type={showFivePaisaUserId ? "text" : "password"}
                    value={fivePaisaUserId}
                    onChange={(e) => setFivePaisaUserId(e.target.value)}
                    placeholder="5paisa USER_ID"
                    suffix={<EyeOutlined onClick={() => setShowFivePaisaUserId(!showFivePaisaUserId)} style={{ cursor: 'pointer' }} />}
                  />
                </Tooltip>
                <Checkbox
                  checked={showFivePaisaUserId}
                  onChange={(e) => setShowFivePaisaUserId(e.target.checked)}
                  style={{ margin: "8px 0 16px" }}
                >
                  Show
                </Checkbox>

                <div style={labelStyle}>5paisa PASSWORD</div>
                <Tooltip title="Different from MPIN! Your 5paisa login password" placement="right" color="#000">
                  <Input
                    type={showFivePaisaLoginPassword ? "text" : "password"}
                    value={fivePaisaLoginPassword}
                    onChange={(e) => setFivePaisaLoginPassword(e.target.value)}
                    placeholder="5paisa login password"
                    suffix={<EyeOutlined onClick={() => setShowFivePaisaLoginPassword(!showFivePaisaLoginPassword)} style={{ cursor: 'pointer' }} />}
                  />
                </Tooltip>
                <Checkbox
                  checked={showFivePaisaLoginPassword}
                  onChange={(e) => setShowFivePaisaLoginPassword(e.target.checked)}
                  style={{ margin: "8px 0 16px" }}
                >
                  Show
                </Checkbox>

                <div style={labelStyle}>User Key (API)</div>
                <Input
                  type={showUserKey ? "text" : "password"}
                  value={userKey}
                  onChange={(e) => setUserKey(e.target.value)}
                  placeholder="5paisa API User Key"
                  suffix={<EyeOutlined onClick={() => setShowUserKey(!showUserKey)} style={{ cursor: 'pointer' }} />}
                />
                <Checkbox
                  checked={showUserKey}
                  onChange={(e) => setShowUserKey(e.target.checked)}
                  style={{ margin: "8px 0 16px" }}
                >
                  Show
                </Checkbox>

                <div style={labelStyle}>App Source (API)</div>
                <Input
                  value={appSource}
                  onChange={(e) => setAppSource(e.target.value)}
                  placeholder="App Source (e.g., 24379)"
                  suffix={<CheckOutlined />}
                  style={{ marginBottom: 16 }}
                />

                <div style={labelStyle}>App Name (Optional)</div>
                <Input
                  value={fivePaisaAppName}
                  onChange={(e) => setFivePaisaAppName(e.target.value)}
                  placeholder="5paisa App Name (optional)"
                  style={{ marginBottom: 16 }}
                />

                <div style={labelStyle}>Encryption Key (Optional)</div>
                <Input
                  value={fivePaisaEncryptionKey}
                  onChange={(e) => setFivePaisaEncryptionKey(e.target.value)}
                  placeholder="5paisa Encryption Key (optional)"
                  style={{ marginBottom: 16 }}
                />
              </>
            )}

            {/* Nickname */}
            <div style={labelStyle}>Pseudo Name (Nickname)</div>
            <Tooltip
              title="A nickname to easily identify the account"
              placement="right"
              color="#000"
            >
              <Input
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                placeholder="Easy to remember nickname"
                suffix={<CheckOutlined />}
                disabled={useLoginAsNickname}
              />
            </Tooltip>

            <Checkbox
              checked={useLoginAsNickname}
              onChange={(e) => setUseLoginAsNickname(e.target.checked)}
              style={{ margin: "8px 0 24px" }}
            >
              Use trading account login id as nickname
            </Checkbox>

            {/* Action Buttons */}
            <Row justify="end" gutter={12}>
              <Col>
                <Button
                  type="primary"
                  icon={<CheckOutlined />}
                  onClick={handleValidate}
                  loading={validating}
                  style={{
                    backgroundColor: isValidated ? "#52c41a" : "#11c26d",
                    borderColor: isValidated ? "#52c41a" : "#11c26d",
                    height: 36,
                    minWidth: 110,
                    borderRadius: 6,
                    fontWeight: 600,
                  }}
                >
                  {isValidated ? "Validated ✓" : "Validate"}
                </Button>
              </Col>

              <Col>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  onClick={handleSave}
                  loading={saving}
                  disabled={!isValidated}
                  style={{
                    backgroundColor: "#00a6a6",
                    borderColor: "#00a6a6",
                    height: 36,
                    minWidth: 110,
                    borderRadius: 6,
                    fontWeight: 600,
                  }}
                >
                  Save
                </Button>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default CreateTradingAccount;

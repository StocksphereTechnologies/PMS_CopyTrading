import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './Components/Navbar.tsx'
import ProtectedRoute from './Components/ProtectedRoute.tsx'
import Login from './Pages/User/Login/Login.tsx'
import Signup from './Pages/User/Signup/Signup.tsx'
import Activity from './Pages/AutoTrader/Activity.tsx'
import MainTabs from './Pages/Trading/Tabs/Tabs.tsx'
import Account from './Pages/User//Account/Account.tsx';
import Profile from './Pages/User/Profile/Profile.tsx';
import Logout from './Pages/User/Logout/Logout.tsx';
import Positions from "./Pages/Trading/Portfolio/Positions.tsx";
import Orders from "./Pages/Trading/Portfolio/Orders.tsx";
import Margins from "./Pages/Trading/Portfolio/Margins.tsx";
import Holdings from "./Pages/Trading/Portfolio/Holdings.tsx";
import Notifications from "./Pages/Trading/Portfolio/Notifications.tsx";
import Screener from "./Pages/Screener/Screener";
import TradingAccounts from "./Pages/Settings/TradingAccounts/TradingAccounts";
import PseudoAccounts from "./Pages/Settings/PseudoAccounts/PseudoAccounts";
import GroupAccounts from "./Pages/Settings/GroupAccounts/GroupAccounts";
import CreateTradingAccount from "./Pages/Settings/TradingAccounts/CreateTradingAccount";
import ValidateAll from './Pages/Settings/TradingAccounts/ValidateAll.tsx';
import CreateGroupAccount from './Pages/Settings/GroupAccounts/CreateGroupAccount.tsx';
import Trade from './Pages/Trading/Trade/Trade.tsx'

const App: React.FC = () => {

  return (
    <>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/" element={<Navigate to="/trading/portfolio" replace />} />

        {/* Protected Routes */}
        <Route path="/*" element={
          <ProtectedRoute>
            <>
              <Navbar />
              <div style={{ padding: 24 }}>
                <Routes>
                  <Route path="/autotrader/activity" element={<Activity />} />
                  <Route path="/trading/portfolio" element={<MainTabs />} />
                  <Route path="/user/account" element={<Account />} />
                  <Route path="/user/profile" element={<Profile />} />
                  <Route path="/user/logout" element={<Logout />} />
                  <Route path="/trading/positions" element={<Positions />} />
                  <Route path="/trading/orders" element={<Orders />} />
                  <Route path="/trading/margins" element={<Margins />} />
                  <Route path="/trading/holdings" element={<Holdings />} />
                  <Route path="/trading/notifications" element={<Notifications />} />
                  <Route path='/Screener/Screener' element={<Screener />} />
                  <Route path="/settings/tradingaccounts" element={<TradingAccounts />} />
                  <Route path="/settings/pseudoaccounts" element={<PseudoAccounts />} />
                  <Route path="/settings/groupaccounts" element={<GroupAccounts />} />
                  <Route path="/settings/tradingaccounts/createtradingaccount" element={<CreateTradingAccount />} />
                  <Route path="/settings/tradingaccounts/validateall" element={<ValidateAll />} />
                  <Route path="/settings/groupaccounts/creategroupaccount/:id?" element={<CreateGroupAccount />} />        
                  <Route path="/trading/trade" element={<Trade />} />        
                </Routes>
              </div>
            </>
          </ProtectedRoute>
        } />
      </Routes>
    </>
  )
}
export default App




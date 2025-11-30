import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import axios from "axios";
import "@/App.css";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { DownloadCloud, Menu, GitBranch, Rocket, Clock, CheckCircle2, XCircle, AlertCircle, TrendingUp, Activity, Github, ArrowLeft } from "lucide-react";
import { AdminLoginPage, AdminDashboardPage } from "./AdminPages";
import { AdminSupportPanel } from "./components/AdminSupportPanel";
import { AdminAutofixPanel } from "./components/AdminAutofixPanel";
import ForAIAssistants from "./pages/ForAIAssistants";

// Imports refactored
import { API } from "@/config/constants";
import { useI18n } from "@/hooks/useI18n";
import { useAuth } from "@/hooks/useAuth";
import { TermsPage } from "@/pages/TermsPage";
import { OAuthCallback } from "@/components/OAuthCallback";
import { SupportChatbot } from "@/components/SupportChatbot";

// TODO: Extract these components to separate files
// These functions are still in this file temporarily
// Lines 266-691: Landing
// Lines 692-938: AuthCard
// Lines 940-2057: Dashboard  
// Lines 2058-2167: ProDashboard
// Lines 2336-2687: AccountPage
// Lines 2688-3206: PricingPage
// Lines 3207-3589: WhitePaperPage

import env from "@/config/env";
import axios from "axios";

const axiosInstance = axios.create({
	baseURL: env.NEXT_PUBLIC_API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

export default axiosInstance;

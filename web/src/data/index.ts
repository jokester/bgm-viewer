import { createContext } from "preact";
import { BGMArchiveAPI } from "./api";
import { useContext } from "preact/hooks";

const apiClient = new BGMArchiveAPI({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

const BgmApiContext = createContext(apiClient)

export const useBgmApi = () => useContext(BgmApiContext)
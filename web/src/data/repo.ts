import { BGMArchiveAPI, Subject } from "./api";

export class BgmDataRepo  {
    constructor(private readonly apiClient: BGMArchiveAPI) {}

    async getSubjectById(id: number) : Promise<Subject | null> {
        const response = await this.apiClient.getSubject(id);
        return response
    }
}
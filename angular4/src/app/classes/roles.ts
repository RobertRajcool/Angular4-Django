export class Roles {
    id: number;
    name: string;
    alias: string;
    created_by: string;
    accesses:string;
    description: string;
    created_at: Date;
    modified_at: Date;
}


export class RolesList {
    constructor(public id : number,
    public text : string){}
}

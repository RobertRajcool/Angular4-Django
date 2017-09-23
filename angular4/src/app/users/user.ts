export class User {
    constructor(public id: number,
        public username: string,
        public email: string,
        public user_type: string,
        public firstName: string,
        public lastName: string,
        public address?: string,
        public description?: string,
        public location?: string,
        public region?: any,
        public vendorCategory?: any,
        public employee_id?:any,
        public roleId?: any,
        public permissions?: any,
        public accesses?: any) { }
}

export class UserType {
    id: number;
    text: string;
}

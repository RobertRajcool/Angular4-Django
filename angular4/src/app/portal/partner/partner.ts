export class Activation {
    constructor(
        public id: number,
        public existing_status: string,
        public jba_code: string,
        public credits: number,
        public preferred_user_name: string
    ) {}
}

export class Rejection {
    constructor(
        public id: number,
        public rejection_reason: string
    ) {}
}

export class Partner {

    constructor(
        public id: number,
        public company_name: string,
        public status: boolean,
        public contact_id: number,
        public name: string,
        public email: string,
        public mobile: number,
        public focused_customer: any,
        public partner_type: any,
        public address_1: string,
        public address_2: string,
        public address_3: string,
        public state: string,
        public city: string,
        public pin_code: number,
        public business_type: any,
        public activated_by: string,
        public interested_workload: any,
        public vendor_list: string,
        public contacts: Array<any>,
        public documents: Array<any>,
        public credits?: number,
        public jba_code?: number,
        public mpn_id?: string,
        public apn_id?: string,
        public apn_id_active?: boolean,
        public user_name?: string,
        public gst_number?: string,
        public partner?: number
    ) {}
}

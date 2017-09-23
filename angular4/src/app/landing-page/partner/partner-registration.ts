export class PartnerRegistration_1 {

    constructor(
        public id: number,
        public company_name: string,
        public name: string,
        public email: string,
        public mobile: string,
        public existing_partner: string,
        public jba_code: string
    ) {}
}

export class PartnerRegistration_2 {

    constructor(
        public id: number,
        public company_name: string,
        public city: string,
        public state: string,
        public pin_code: string,
        public addrs_line_1: string,
        public addrs_line_2: string,
        public addrs_line_3 : string,
        public director_cntct_status: string,
        public director_name: string,
        public director_email: string,
        public director_mobile: string,
        public accts_cntct_status: string,
        public accts_name: string,
        public accts_email: string,
        public accts_mobile: string,
        public sales_cntct_status: string,
        public sales_name: string,
        public sales_email: string,
        public sales_mobile: string,
        public preferred_user_name: string,
        public terms_and_cndtns_status: string,
        public documents: Array<any>,
        public gst_number: string
    ) {}
}

export class PartnerRegistration_3 {

    constructor(
        public id: number,
        public partner_type: Array<any>,
        public core_business: any,
        public focused_customer: any,
        public interested_workloads: any
    ) {}
}

export function PartnerType() {
    let types: Array<any> = [
        { id: 1, text: 'Reseller', symbol: 'R', checked: false},
        { id: 2, text: 'Consulting & Implementation', symbol: 'C&I', checked: false},
        { id: 3, text: 'Managed Service Provider', symbol: 'MSP', checked: false},
        { id: 4, text: 'Technology Partner', symbol: 'TP', checked: false}
    ];

    return types;
}

export function PartnerDocumentType() {
    let types: Array<any> = [
        { id: 1, text: 'Last 3 months bank statement', type: 'Bank statement', symbol: 'bank_statement', checked: false},
        { id: 2, text: 'Latest Audit Accounts with Income Tax return acknowledgement copy', type: 'Audits', symbol: 'income_tax', checked: false},
        { id: 3, text: 'CST &amp; LST Registration proof', type: 'CST & LST', symbol: 'cst_lst', checked: false},
        { id: 4, text: 'Memorandum &amp; Articles of Association/Partnership Agreements', type: 'Memorandum & Articles', symbol: 'memorandum_proof', checked: false},
        { id: 5, text: 'Copy of Passport of Proprietor/Partner/Directors (Mandatory)', type: 'Passport', symbol: 'passport', checked: false},
        { id: 6, text: 'Company PAN Card (Mandatory)', type: 'Pan card', symbol: 'pan_card', checked: false},
        { id: 7, text: 'GST Registration Certificate (Mandatory)', type: 'GST certificate', symbol: 'service_tax', checked: false}
    ];

    return types;
}

export function CoreBusinessItems() {
    let items: Array<any> = [
        { id: 1, text: 'Hardware' },
        { id: 2, text: 'Software' },
        { id: 3, text: 'Services' },
        { id: 4, text: 'App Development' },
        { id: 5, text: 'Security' },
        { id: 6, text: 'Cloud' }
    ];

    return items;
}

export function InterestedWorkLoadsItems() {
    let items: Array<any> = [
        { id: 1, text: 'Website & Web apps' },
        { id: 2, text: 'Backup Storage Archive' },
        { id: 3, text: 'Disaster Recovery' },
        { id: 4, text: 'Hosting' },
        { id: 5, text: 'Mailing solution' },
        { id: 6, text: 'IT Asset management' },
        { id: 7, text: 'Consulting services' },
        { id: 8, text: 'Migration Services' },
        { id: 9, text: 'Support & Ticketing services' },
        { id: 10, text: 'Video conferencing' },
        { id: 11, text: 'Customer relationship management' },
        { id: 12, text: 'Other Services' }
    ];

    return items;
}

export function CustomerItems() {
    let items: Array<any> = [
        { id: 1, text: 'Airlines, Aviation & Defence' },
        { id: 2, text: 'Automobile' },
        { id: 3, text: 'BFSI' },
        { id: 4, text: 'Cement' },
        { id: 5, text: 'Marble' },
        { id: 6, text: 'Stone Etc.,' },
        { id: 7, text: 'Chemical' },
        { id: 8, text: 'Construction' },
        { id: 9, text: 'Consulting' },
        { id: 10, text: 'Consumer Durables' },
        { id: 11, text: 'Home appliances' },
        { id: 12, text: 'Courier' },
        { id: 13, text: 'Logistics' },
        { id: 14, text: 'Packages' },
        { id: 15, text: 'E-commerce' },
        { id: 16, text: 'Education' },
        { id: 17, text: 'Electrical & Electronics' },
        { id: 18, text: 'Engineering' },
        { id: 19, text: 'Entertainment' },
        { id: 20, text: 'Export & Import' },
        { id: 21, text: 'Facility Management' },
        { id: 22, text: 'FMCG' },
        { id: 23, text: 'Agriculture' },
        { id: 24, text: 'Hospital' },
        { id: 25, text: 'Healthcare' },
        { id: 26, text: 'Hospitality' },
        { id: 27, text: 'Information Technology' },
        { id: 28, text: 'ITES' },
        { id: 29, text: 'BPO' },
        { id: 30, text: 'KPO' },
        { id: 31, text: 'Jewellery' },
        { id: 32, text: 'Manufacturing' },
        { id: 33, text: 'Marine' },
        { id: 34, text: 'NGO' },
        { id: 35, text: 'Retail' },
        { id: 36, text: 'Service Industry' },
        { id: 37, text: 'Telecommunication' },
        { id: 38, text: 'Textile' },
        { id: 39, text: 'Travel & Tourism' }
    ];

    return items;
}
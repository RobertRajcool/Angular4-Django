export class Customers {
    id: number;
    company_name: string;
    logo: string;
    address: string;
    city: string;
    state: string;
    country: string;
    pan_number: string;
    contacts?: Array<any>;
    partner? : string;
}


// Customer cloud accounts
export class CustomerCloudAccount {
    url: string;
    id: number;
    customer: any;
    vendor: any;
    active: boolean;
    type: string;
    details: AwsCloudAccountDetails | MsCloudAccountDetails | Object;
    licenses_and_credentials: any;
    created_by: any;
    created_at: Date;
    modified_by: any;
    modified_at: Date;

    constructor(data?: Object, accountType?: string) {
        if (!accountType && data) accountType = data['type'];

        switch (accountType) {
            case "AWS":
                if (data) this.details = new AwsCloudAccountDetails(data['details']);
                else this.details = new AwsCloudAccountDetails();
                break;
            case "MS":
                if (data) this.details = new MsCloudAccountDetails(data['details']);
                else this.details = new MsCloudAccountDetails();
                break;
            default:
                this.details = {}; break;
        }

        if (data) {
            this.url = data['url'] || '';
            this.id = data['id'] || '';
            this.customer = data['customer'] || '';
            this.vendor = data['vendor'] || '';
            this.active = data['active'] || '';
            this.type = data['type'] || '';
            this.licenses_and_credentials = data['licenses_and_credentials'] || '';
            this.created_at = data['created_at'] || '';
            this.created_by = data['created_by'] || '';
            this.modified_at = data['modified_at'] || '';
            this.modified_by = data['modified_by'] || '';
        }
    }
}

// For AWS
class AwsCloudAccountDetails {
    account_id: string;
    friendly_name: string;
    iam_username: string;
    iam_password: string;
    iam_url: string;
    allow_order: string;

    constructor(data?: Object) {
        this.account_id = this.friendly_name = this.iam_username = this.iam_password = this.allow_order = this.iam_url = '';

        if (data) {
            this.account_id = data['account_id'] || '';
            this.friendly_name = data['friendly_name'] || '';
            this.iam_username = data['iam_username'] || '';
            this.iam_password = data['iam_password'] || '';
            this.iam_url = data['iam_url'] || '';
            this.allow_order = data['allow_order'] || '';
        }
    }
}

// For Microsoft
class MsCloudAccountDetails {
    domain_name: string;
    allow_order: string;
    standard_discount: string;

    constructor(data?: Object) {
        this.domain_name = '';
        this.allow_order = '';
        this.standard_discount = '';
        if (data) {
            this.domain_name = data['domain_name'] || '';
            this.standard_discount = data['standard_discount'] || '';
        }
    }
}

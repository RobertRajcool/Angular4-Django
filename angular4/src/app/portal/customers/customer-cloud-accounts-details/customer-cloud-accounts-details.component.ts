import { Component, OnInit, OnDestroy, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CustomerCloudAccount } from 'app/classes';
import { CustomerCloudAccountsService } from 'app/services';

@Component({
    selector: 'app-customer-cloud-accounts-details',
    templateUrl: './customer-cloud-accounts-details.component.html'
})
export class CustomerCloudAccountsDetailsComponent implements OnInit {
    @Input('title') pageTitle: string = 'Cloud Accounts';
    _cloudAccounts: Array<CustomerCloudAccount> = [];
    subscriptions: Object = {};

    constructor(
        private route: ActivatedRoute,
        private ccaService: CustomerCloudAccountsService
    ) {
        // Route data subscriptions
        this.subscriptions['routeDataSubscription'] = this.route.params.subscribe(params => {
            this.fetchCloudAccounts(params['id']);
        })
    }

    ngOnInit() {
    }

    @Input('cloudAccounts')
    set cloudAccounts(data: Array<CustomerCloudAccount>) {
        this._cloudAccounts = data; 
    }

    fetchCloudAccounts(customer_id?: number) {
        let queryParams: Object = {
            "customer_id": customer_id,
            "order_by": "type",
            "form_data": true
        }

        this.ccaService.listCloudAccounts(queryParams)
            .subscribe(Result => {
                this.cloudAccounts = Result['records']; 
            }, Error => {
                console.log(Error);
            })
    }
    // unsubscribing subscriptions
    ngOnDestroy() {
        Object.keys(this.subscriptions).forEach(property => {
            this.subscriptions[property].unsubscribe();
        })
    }

}

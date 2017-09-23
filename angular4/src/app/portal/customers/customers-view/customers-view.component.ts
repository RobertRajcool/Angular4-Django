import { Component, OnInit, ViewEncapsulation, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs/Subscription';
import { Customers } from 'app/classes';
import { CustomersService } from 'app/services';
import { GetApiurl } from 'app/parameters';

@Component({
    selector: 'app-customers-view',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './customers-view.component.html',
    styleUrls: ['./customers-view.component.scss']
})
export class CustomersViewComponent implements OnInit {
    subscritptions: Object = {};
    customerDetails: Customers;
    routeurl: any;
    customerid: number;
    partnerid: any;
    status: any;
    panStatus = false;

    public fetchUrl: string;
    public addButtonInfo: Object = {};
    public commonFilter: Object = {};
    public columns: Array<any> = [
        { title: 'Order ID', name: 'order_number', sort: false },
        { title: 'Product detail', name: 'details', sort: false },
        { title: 'Price', name: 'total_cost', sort: false },
        { title: 'Status', name: 'status', sort: false },
        { title: 'Actions', links: ['View'] }
    ];

    routeParams: Object = {
        id: 0,
        tab: 'details'
    };

    constructor(
        private route: ActivatedRoute,
        private router: Router,
        private customerService: CustomersService
    ) {

        this.subscritptions['urlSubscription'] = this.router
            .events
            .filter(event => event instanceof NavigationEnd)
            .subscribe((event: NavigationEnd) => {
                this.routeurl = event.url;
            });

        this.subscritptions['routeParamsSubscription'] = this.route.params.subscribe(params => {
            this.routeParams = params;
            this.customerid = params['id'];
            this.partnerid = params['partnerid'];
            this.fetchUrl = GetApiurl(`orders/customer/${this.customerid}/`);
            if (params['id']) this.getCustomerDetails(params['id']);
        })
    }

    ngOnInit() { }

    getCustomerDetails(id: number) {
        if (this.routeurl && this.routeurl.split('/')[2] == 'customers') {
            this.status = 'customer view'
        }
        else {
            this.status = 'partner customer view'
        }
        this.customerService.getCustomer(id)
            .subscribe(
            Result => {
                this.customerDetails = Result;
                localStorage.setItem('customer_name', this.customerDetails.company_name);

                if (this.customerDetails['pan_number'] != '') {
                    this.panStatus = true
                }
            },
            Error => console.log(Error)
            );
    }
    orders() {
        if (this.routeurl && this.routeurl.split('/')[2] == 'customers') {
            this.router.navigate(['/app/customers/' + this.customerid + '/orders']);
        }
        else {
            this.router.navigate(['/app/partner/' + this.partnerid + '/customers/' + this.customerid + '/view/orders']);
        }

    }
    details() {
        if (this.routeurl && this.routeurl.split('/')[2] == 'customers') {
            this.router.navigate(['/app/customers/' + this.customerid + '/details']);
        }
        else {
            this.router.navigate(['/app/partner/' + this.partnerid + '/customers/' + this.customerid + '/view/details']);
        }
    }
    invoices() {
        if (this.routeurl && this.routeurl.split('/')[2] == 'customers') {
            this.router.navigate(['/app/customers/' + this.customerid + '/invoices']);
        }
        else {
            this.router.navigate(['/app/partner/' + this.partnerid + '/customers/' + this.customerid + '/view/invoices']);
        }

    }
    cloudAccounts() {
        if (this.routeurl && this.routeurl.split('/')[2] == 'customers') {
            this.router.navigate(['/app/customers/' + this.customerid + '/cloud-accounts']);
        }
        else {
            this.router.navigate(['/app/partner/' + this.partnerid + '/customers/' + this.customerid + '/view/cloud-accounts']);
        }

    }

    BackToList() {
        if (this.routeurl && this.routeurl.split('/')[2] == 'customers') {
            this.router.navigate(['/app/customers/list']);
        }
        else {
            this.router.navigate(['/app/partner/' + this.partnerid + '/customers/']);
        }

    }

    eventListener(event: any) {
        let data = event.data;
        if (data.action == 'View') {
            let url: string = "/app/orders/" + data.row.id;
            this.router.navigateByUrl(url);
        }
    }
    ngOnDestroy() {
        Object.keys(this.subscritptions).forEach(subscriptionName => {
            this.subscritptions[subscriptionName].unsubscribe();
        })
    }
}

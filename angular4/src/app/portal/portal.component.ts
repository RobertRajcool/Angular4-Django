import { Component, ViewEncapsulation, ElementRef, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { AppConfig, GlobalsService } from 'app/services';
import { Subscription } from 'rxjs/Subscription';
import { RedingtonErrorService } from 'app/services/redington.error.service';
import {  BreadcrumbService } from 'app/directives/ng2-breadcrumb/breadcrumb.service';
declare var jQuery: any;
declare var Hammer: any;
declare var Raphael: any;

@Component({
    selector: 'app-portal',
    encapsulation: ViewEncapsulation.None,
    templateUrl: './portal.component.html',
    styleUrls: [
        './portal.component.scss'
    ],
    host: {
        '[class.nav-static]': 'config.state["nav-static"]',
        '[class.chat-sidebar-container]': 'cartOpened',
        '[class.chat-sidebar-opened]': 'cartOpened',
        '[class.app]': 'true',
        id: 'app',
    }
})
export class PortalComponent implements OnInit {
    config: any;
    configFn: any;
    $sidebar: any;
    el: ElementRef;
    router: Router;
    chatOpened: boolean = false;
    toastMessage: Array<string> = ['', 'success'];
    public errorMsg: string;
    public iserrorStatus: boolean = false;
    cartOpened: boolean = false;
    subscriptions: Object = {};


    constructor(
        router: Router,
        config: AppConfig,
        el: ElementRef,
        private gs: GlobalsService,
        private errorservice: RedingtonErrorService,
        private breadcrumbService:BreadcrumbService
    ) {
        Raphael.prototype.safari = function (): any { return; };
        this.el = el;
        this.config = config.getConfig();
        this.configFn = config;
        this.router = router;
        breadcrumbService.addFriendlyNameForRoute('/app', 'Home');
        breadcrumbService.addFriendlyNameForRoute('/app/dashboard', 'Dashboard');
        breadcrumbService.addFriendlyNameForRoute('/app/profile', 'Profile');
        breadcrumbService.addFriendlyNameForRoute('/app/subscription', 'Subscriptions');
        breadcrumbService.addFriendlyNameForRoute('/app/ms-send-so', 'Process SO');
        breadcrumbService.addFriendlyNameForRoute('/app/pending-request', 'Account request');
        breadcrumbService.addFriendlyNameForRoute('/app/update-mpn', 'Update MPN ID');
        breadcrumbService.addFriendlyNameForRoute('/app/users', 'Users');
        breadcrumbService.addFriendlyNameForRoute('/app/users/roles', 'Manage roles');
        breadcrumbService.addFriendlyNameForRoute('/app/users/addUser', 'Add User');
        breadcrumbService.addFriendlyNameForRoute('/app/orders/pending', 'Waiting for Approval');
        breadcrumbService.addFriendlyNameForRoute('/app/orders/rejected', 'Rejected Orders');
        breadcrumbService.addFriendlyNameForRoute('/app/cloudtemplates/listInstances', 'Instances');
        breadcrumbService.addFriendlyNameForRoute('/app/cloudtemplates/listStorages', 'Storages');
        breadcrumbService.addFriendlyNameForRoute('/app/customers', 'Customers');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/customers/add*', 'Add customer');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/orders$', 'Orders');
        breadcrumbService.addFriendlyNameForRoute('/app/orders/approved', 'Approved orders');
        breadcrumbService.addFriendlyNameForRoute('/app/orders/waiting-for-invoice', 'Waiting for invoice');
        breadcrumbService.addFriendlyNameForRoute('/app/cloudtemplates', 'Cloud templates');
        breadcrumbService.addFriendlyNameForRoute('/app/cloudtemplates/add', 'Add new template');
        breadcrumbService.addFriendlyNameForRoute('/app/cloudtemplates/key-pairs', 'Key Pairs');
        breadcrumbService.addFriendlyNameForRoute('/app/vendor', 'Vendors');
        breadcrumbService.addCallbackForRouteRegex('/app/vendor/[0-9]', this.getVendorName);
        breadcrumbService.addCallbackForRouteRegex('/app/vendor/view/[0-9]', this.getVendorName);
        breadcrumbService.addCallbackForRouteRegex('/app/cloudtemplates/create/[0-9]', this.getCloudTemplate);
        breadcrumbService.addFriendlyNameForRoute('/app/product', 'Products');
        breadcrumbService.addCallbackForRouteRegex('/app/product/viewproduct/[0-9]', this.gedViewProductName);
        breadcrumbService.addCallbackForRouteRegex('/app/product/editproduct/[0-9]', this.gedEditProductName);
        breadcrumbService.addFriendlyNameForRoute('/app/product/addproductcsv', 'Add product CSV')
        //breadcrumbService.addFriendlyNameForRouteRegex('/app/product*', 'Products');
        breadcrumbService.addFriendlyNameForRoute('/app/product/addproduct', 'Add product');
        breadcrumbService.addFriendlyNameForRoute('/app/vendor/addvendor', 'Add vendor');
        breadcrumbService.addFriendlyNameForRoute('/app/offers', 'Business offer');
        breadcrumbService.addCallbackForRouteRegex('/app/offers/[0-9]$', this.getOffer);
        breadcrumbService.addCallbackForRouteRegex('/app/offers/editoffer/[0-9]$', this.getOffer);
        breadcrumbService.addFriendlyNameForRoute('/app/offers/addoffer', 'Add offer');
        breadcrumbService.addFriendlyNameForRoute('/app/notification-groups', 'Notification groups');
        breadcrumbService.addFriendlyNameForRoute('/app/notification-actions', 'Notification actions');
        breadcrumbService.addFriendlyNameForRoute('/app/partner', 'Partners');
        breadcrumbService.addFriendlyNameForRoute('/app/inactive-partner', 'Partners to activate');
        breadcrumbService.addFriendlyNameForRoute('/app/rejected-partner', 'Rejected partners');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner-profile/[0-9]*$', 'Partner Profile');
        breadcrumbService.addCallbackForRouteRegex('/app/partner/[0-9]*$', this.getNameForPartner);
        breadcrumbService.addCallbackForRouteRegex('/app/inactive-partner/[0-9]$', this.getNameForPartner);
        breadcrumbService.addCallbackForRouteRegex('/app/customers/[0-9]*$', this.getCustomerName);
        breadcrumbService.addFriendlyNameForRouteRegex('/app/customers/[0-9]*/details', 'Details');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner/[0-9]*/details', 'Details');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner/[0-9]/customers', 'Customers');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner/[0-9]/add_customer', 'Add customer');
        breadcrumbService.addCallbackForRouteRegex('/app/partner/[0-9]*/customers/[0-9]*$', this.getCustomerName);
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner/[0-9]/customers/[0-9]/view/orders', 'Orders');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/notifications/*', 'Notifications');
        breadcrumbService.addCallbackForRouteRegex('/app/orders/ms-send-so/view/[0-9]*$', this.getViewOrder);
        breadcrumbService.addFriendlyNameForRouteRegex('/app/ms-send-so/view/[0-9]', 'ms-send-so');
        breadcrumbService.addFriendlyNameForRoute('/app/rejected-partner/list', 'Rejected Partners');
        // Cloud tempalte and instance
        breadcrumbService.hideRoute('/app/cloudtemplates/view');
        breadcrumbService.addCallbackForRouteRegex('/app/cloudtemplates/view/[0-9]', this.getTempalteName);
        breadcrumbService.hideRoute('/app/cloudtemplates/instance');
        breadcrumbService.addCallbackForRouteRegex('/app/cloudtemplates/instance/[0-9]', this.getInstanceId);

        // AWS Credits and APN update
        breadcrumbService.addFriendlyNameForRoute('/app/activate-apn-account', 'Activate APN account');
        breadcrumbService.addFriendlyNameForRoute('/app/aws-credits', 'AWS credits');
        breadcrumbService.addCallbackForRouteRegex('/app/aws-credits/[0-9]+$', this.getCreditCustomerName);
        breadcrumbService.addFriendlyNameForRoute('/app/update-apn', 'Update APN');

        breadcrumbService.addFriendlyNameForRoute('/app/users/list', 'Users');
        breadcrumbService.addCallbackForRouteRegex('/app/users/[0-9]', this.getUserName);
        breadcrumbService.addCallbackForRouteRegex('/app/orders/[0-9]+$', this.getOrderNumber);
        breadcrumbService.addCallbackForRouteRegex('/app/orders/pending/view/[0-9]', this.getViewOrder);
        breadcrumbService.addCallbackForRouteRegex('/app/orders/approved/view/[0-9]', this.getViewOrder);
        breadcrumbService.addCallbackForRouteRegex('/app/orders/pending/approve/[0-9]', this.getApproveOrder);
        breadcrumbService.addCallbackForRouteRegex('/app/orders/waiting-for-invoice/view/[0-9]', this.getOrderNumber);
        breadcrumbService.addCallbackForRouteRegex('/app/orders/rejected/view/[0-9]', this.getRejectedOrder);
        breadcrumbService.addFriendlyNameForRouteRegex('/app/orders/pending/[0-9]/view', 'View');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/orders/[0-9]+/amend-order', 'Amend order');
        breadcrumbService.addCallbackForRouteRegex('/app/users/view/[0-9]', this.getUserName);
        breadcrumbService.addFriendlyNameForRoute('/app/reports/overallsales_vendor', 'SaaS Vendor Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/overallsales_cloud', 'Sales Cloud Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/productsales_reports', 'Product Sales by Vendor');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/product_report', 'Product Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/overallsales_report', 'Overall sales Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/zonewise_report', 'Zone-wise Sales Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/order_reports', 'Order Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/order_customers', 'Orders List');
        breadcrumbService.addFriendlyNameForRoute('/app/feedback', 'Support');
        breadcrumbService.addFriendlyNameForRoute('/app/change-password', 'Change Password');
        breadcrumbService.hideRoute('/app/softlayer');
        breadcrumbService.addFriendlyNameForRoute('/app/softlayer/quotes', 'Softlayer Quotes');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/product*', 'Products');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/customer_reports', 'Customer Growth Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/partner_reports', 'Partner Growth Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/customer_segmentation_report', 'Customer Segmentation Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/transacting_partners', 'Transacting Partner Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/aws_mrr_report', 'AWS MRR Trend Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/partner_segmentation_report', 'Partner Segmentation Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/customer_reports', 'Customer Growth Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/partner_reports', 'Partner Growth Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/customer_segmentation_report', 'Partner Segmentation Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/transacting_partners', 'Transacting Partner Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/reports/aws_mrr_report', 'AWS MRR Trend Reports');
        breadcrumbService.addFriendlyNameForRoute('/app/trial_accounts','Trial Accounts');
        breadcrumbService.addFriendlyNameForRoute('/app/trial_accounts/list','Trial Accounts');
        breadcrumbService.addCallbackForRouteRegex('/app/trial_accounts/view/[0-9]',this.getTrialAccountName);




        breadcrumbService.hideRoute('/app/cloudtemplates/create');
        breadcrumbService.hideRoute('/app/cloudtemplates/create');
        breadcrumbService.hideRoute('/app/vendor/view');
        breadcrumbService.hideRoute('/app/orders/pending/approve');
        breadcrumbService.hideRoute('/app/orders/pending/view');
        breadcrumbService.hideRoute('/app/orders/ms-send-so/view');
        breadcrumbService.hideRoute('/app/orders/ms-send-so')
        breadcrumbService.hideRoute('/app/orders/approved/view');
        breadcrumbService.hideRoute('/app/orders/waiting-for-invoice/view');
        breadcrumbService.hideRoute('/app/orders/rejected/view');
        breadcrumbService.hideRoute('/app/partner/list');
        breadcrumbService.hideRoute('/app/rejected-partner/list');
        breadcrumbService.hideRoute('/app/product/viewproduct');
        breadcrumbService.hideRoute('/app/product/editproduct');
        breadcrumbService.hideRouteRegex('/app/notifications/messages/*');
        breadcrumbService.hideRouteRegex('/app/notifications/alerts/*');
        breadcrumbService.hideRouteRegex('/app/partner/[0-9]*/customers/[0-9]*/view$');
        breadcrumbService.hideRouteRegex('/app/offers/editoffer$');
        breadcrumbService.hideRouteRegex('/app/partner/[0-9]*/customers/[0-9]*/view/details');
        breadcrumbService.hideRouteRegex('app/inactive-partner/[0-9]/activate');
        breadcrumbService.hideRoute('/app/partner-profile');
        breadcrumbService.hideRoute('/app/reports');
        breadcrumbService.hideRoute('/app/inactive-partner/list');
        breadcrumbService.hideRoute('/app/customers/list');
        breadcrumbService.hideRoute('/app/users/list');
        //breadcrumbService.hideRouteRegex('/app/orders/pending-orders/[0-9]/view');
        breadcrumbService.hideRoute('/app/users/view');
        breadcrumbService.hideRoute('/app/reports');
        breadcrumbService.hideRoute('app/rejected-partner');
        breadcrumbService.hideRoute('/app/trial_accounts/list');
        breadcrumbService.hideRoute('/app/trial_accounts/view');



        // Market Place
        breadcrumbService.addFriendlyNameForRoute('/app/market-place', 'Market place');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/market-place/vendors*', 'Vendors');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/market-place/[A-Za-z]+/products$', 'Products');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/market-place/[A-Za-z]+/advanced$', 'Advanced');
        breadcrumbService.hideRouteRegex('/app/market-place/[A-Za-z]+/products/[0-9]+/details*');

        breadcrumbService.hideRouteRegex('/app/market-place/isv-products/[0-9]+');

        // Bills  isv-products/1/view
        breadcrumbService.hideRoute('/app/bills');
        breadcrumbService.hideRouteRegex('/app/bills/[A-Z]+$');
        breadcrumbService.addFriendlyNameForRoute('/app/bills/AWS/consolidated-bill', 'AWS consolidated bill');
        breadcrumbService.addFriendlyNameForRoute('/app/bills/AZURE/consolidated-bill', 'Azure consolidated bill');

        // AWS Details
        breadcrumbService.addFriendlyNameForRoute('/app/aws', 'AWS');
        breadcrumbService.hideRoute('/app/aws/accounts');
        breadcrumbService.addFriendlyNameForRoute('/app/aws/accounts/linked', 'Account Linked');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/aws/accounts/[0-9]+/details', 'Details');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/aws/accounts/[0-9]+/linking', 'Linking');

        // Invoices
        breadcrumbService.addFriendlyNameForRoute('/app/invoices', 'Invoices');
        breadcrumbService.addFriendlyNameForRoute('/app/invoices/list', 'List');
        breadcrumbService.addFriendlyNameForRoute('/app/invoices/aws-sales-orders', 'AWS sales orders');
        breadcrumbService.addFriendlyNameForRoute('/app/invoices/azure-sales-orders', 'Azure sales orders');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/invoices/[A-Za-z]+/[A-Z0-9a-z]+/send-sales-order*', 'Send sales order');
        breadcrumbService.hideRouteRegex('/app/invoices/[A-Za-z]+/[A-Z0-9a-z]+$');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/customers/[0-9]+/invoices', 'Invoices');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner/[0-9]+/customers/[0-9]+/view/invoices', 'Invoices');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner/[0-9]+/invoices', 'Invoices');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/invoices/payment*', 'Payments')

        // Renewal subscription
        breadcrumbService.addFriendlyNameForRoute('/app/renewal-subscription', 'Renewal Subscription');

        // Advance payment
        breadcrumbService.hideRoute('/app/advance-payment/list');
        breadcrumbService.addFriendlyNameForRoute('/app/advance-payment', 'Payment');
        // Downgrade subscription
        breadcrumbService.addFriendlyNameForRoute('/app/downgrade-subscription', 'Downgrade request');

        // ECB Process
        breadcrumbService.addFriendlyNameForRoute('/app/customer-registration-link', 'Send Registration Link');
        breadcrumbService.addFriendlyNameForRoute('/app/orc-linking', 'ORC Linking');
        breadcrumbService.hideRoute('/app/partner-customers');
        breadcrumbService.addFriendlyNameForRoute('/app/partner-customers/active', 'Active Customers');
        breadcrumbService.addFriendlyNameForRoute('/app/partner-customers/inactive', 'In-Active Customers');
        breadcrumbService.addCallbackForRouteRegex('/app/partner-customers/[0-9]*$', this.getNameForPartner);
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner-customers/[0-9]*/details', 'Details');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner-customers/[0-9]*/customers', 'Customers');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner-customers/[0-9]*/invoices', 'Invoices');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner-customers/[0-9]*/orders', 'Orders');
        breadcrumbService.addFriendlyNameForRouteRegex('/app/partner-customers/[0-9]*/activate', 'Activate');

        // Cloud Instances
        breadcrumbService.addFriendlyNameForRoute('/app/cloud-instances', 'Instances');
        breadcrumbService.addFriendlyNameForRoute('/app/cloud-instances/list', 'List');
        breadcrumbService.addCallbackForRouteRegex('/app/cloud-instances/[0-9]*$', this.getInstanceName);

        this.subscriptions['user_subscription'] = this.gs.user$.subscribe(data => {

            if (data) {
                if (data.user_type != 'P') {
                    breadcrumbService.hideRoute('/app/orders');
                } else {
                    breadcrumbService.hideRoute('/app/cloudtemplates');
                }
            }
        });
    }

    getNameForPartner(id: string): string {
        let name = localStorage.getItem('partner_name');
        return name;
    }

    getOrderNumber(id: string): string {
        let name = localStorage.getItem('order_number');
        return name;
    }

    getViewOrder(id: string): string {
        let name = localStorage.getItem('order_number') + '  -  View';
        return name;
    }

    getApproveOrder(id: string): string {
        let name = localStorage.getItem('order_number') + '  >  Approve';
        return name;
    }
    getRejectedOrder(id: string): string {
        let name = localStorage.getItem('order_number');
        return name;
    }

    getOffer(id: string): string {
        let name = localStorage.getItem('offer');
        return name;
    }

    getCloudTemplate(id: string): string {
        let name = 'Create: ' + localStorage.getItem('cloud_product');
        return name;
    }

    gedViewProductName(id: string): string {
        let name = localStorage.getItem('product_name') + '  >  View';
        return name;
    }

    gedEditProductName(id: string): string {
        let name = localStorage.getItem('product_name') + '  >  Edit';
        return name;
    }

    getCustomerName(id: string): string {
        let name = localStorage.getItem('customer_name');
        return name;
    }

    getCreditCustomerName(id: string): string {
        let name = localStorage.getItem('credit_customer_name');
        return name;
    }

    getVendorName(id: string): string {
        let name = localStorage.getItem('vendor_name');
        return name;
    }
    getUserName(id: string): string {
        let name = localStorage.getItem('username');
        return name;
    }

    getInstanceName(id: string): string {
        let name = localStorage.getItem('instance_name');
        return name;

    }
    getTempalteName(id: string): string {
        let name = localStorage.getItem('template_name') + '  >  View';
        return name;

    }
    getInstanceId(id: string): string {
        let name = 'Instances'+'  '+'>'+localStorage.getItem('instance_id') + '  >  View';
        return name;

    }
    getTrialAccountName(id: string):string{
      let name = localStorage.getItem('trial_name')
      return name;
    }



    toggleSidebarListener(state): void {
        let toggleNavigation = state === 'static'
            ? this.toggleNavigationState
            : this.toggleNavigationCollapseState;
        toggleNavigation.apply(this);
        localStorage.setItem('nav-static', this.config.state['nav-static']);
    }

    // Toggling cart sidebar
    toggleCartListener(): void {
        //this.cartService.toggleCartSidebar();
    }

    toggleChatListener(): void {
        jQuery(this.el.nativeElement).find('.chat-notification-sing').remove();
        this.chatOpened = !this.chatOpened;

        setTimeout(() => {
            // demo: add class & badge to indicate incoming messages from contact
            // .js-notification-added ensures notification added only once
            jQuery('.chat-sidebar-user-group:first-of-type ' +
                '.list-group-item:first-child:not(.js-notification-added)')
                .addClass('active js-notification-added')
                .find('.fa-circle')
                .after('<span class="badge tag-danger ' +
                'pull-right animated bounceInDown">3</span>');
        }, 1000);
    }

    toggleNavigationState(): void {
        this.config.state['nav-static'] = !this.config.state['nav-static'];
        if (!this.config.state['nav-static']) {
            this.collapseNavigation();
        }
    }

    expandNavigation(): void {
        // this method only makes sense for non-static navigation state
        if (this.isNavigationStatic()
            && (this.configFn.isScreen('lg') || this.configFn.isScreen('xl'))) { return; }

        jQuery('app-portal').removeClass('nav-collapsed');
        this.$sidebar.find('.active .active').closest('.collapse').collapse('show')
            .siblings('[data-toggle=collapse]').removeClass('collapsed');
    }

    collapseNavigation(): void {
        // this method only makes sense for non-static navigation state
        if (this.isNavigationStatic()
            && (this.configFn.isScreen('lg') || this.configFn.isScreen('xl'))) { return; }

        jQuery('app-portal').addClass('nav-collapsed');
        this.$sidebar.find('.collapse.in').collapse('hide')
            .siblings('[data-toggle=collapse]').addClass('collapsed');
    }

    /**
     * Check and set navigation collapse according to screen size and navigation state
     */
    checkNavigationState(): void {
        if (this.isNavigationStatic()) {
            if (this.configFn.isScreen('sm')
                || this.configFn.isScreen('xs') || this.configFn.isScreen('md')) {
                this.collapseNavigation();
            }
        } else {
            if (this.configFn.isScreen('lg') || this.configFn.isScreen('xl')) {
                setTimeout(() => {
                    this.collapseNavigation();
                }, this.config.settings.navCollapseTimeout);
            } else {
                this.collapseNavigation();
            }
        }
    }

    isNavigationStatic(): boolean {
        return this.config.state['nav-static'] === true;
    }

    toggleNavigationCollapseState(): void {
        if (jQuery('app-portal').is('.nav-collapsed')) {
            this.expandNavigation();
        } else {
            this.collapseNavigation();
        }
    }

    _sidebarMouseEnter(): void {
        if (this.configFn.isScreen('lg') || this.configFn.isScreen('xl')) {
            this.expandNavigation();
        }
    }
    _sidebarMouseLeave(): void {
        if (this.configFn.isScreen('lg') || this.configFn.isScreen('xl')) {
            this.collapseNavigation();
        }
    }

    enableSwipeCollapsing(): void {
        let swipe = new Hammer(document.getElementById('content-wrap'));
        let d = this;

        swipe.on('swipeleft', () => {
            setTimeout(() => {
                if (d.configFn.isScreen('md')) { return; }

                if (!jQuery('app-portal').is('.nav-collapsed')) {
                    d.collapseNavigation();
                }
            });
        });

        swipe.on('swiperight', () => {
            if (d.configFn.isScreen('md')) { return; }

            if (jQuery('app-portal').is('.chat-sidebar-opened')) { return; }

            if (jQuery('app-portal').is('.nav-collapsed')) {
                d.expandNavigation();
            }
        });
    }

    collapseNavIfSmallScreen(): void {
        if (this.configFn.isScreen('xs')
            || this.configFn.isScreen('sm') || this.configFn.isScreen('md')) {
            this.collapseNavigation();
        }
    }

    ngOnInit(): void {


        this.subscriptions['toastMessageSubscription'] = this.gs.toastMessage.subscribe(message => {
            this.toastMessage = message;
        });

        this.subscriptions['errormsgsubscription'] = this.errorservice.getEmittedValue().subscribe(event => {
            this.errorMsg = event.errordata
            this.iserrorStatus = event.statusvalue
        });

        // Cart Sidebar toggle event
        /* this.subscriptions['cartStatusSourceSubscription'] = this.cartService.cartStatus$.subscribe(statuses => {
            if (statuses.indexOf('cartsidebar-opened') >= 0) this.cartOpened = true;
            else this.cartOpened = false;
        }) */

        if (localStorage.getItem('nav-static') === 'true') {
            this.config.state['nav-static'] = true;
        }

        let $el = jQuery(this.el.nativeElement);
        this.$sidebar = $el.find('[sidebar]');

        this.router.events.subscribe((event) => {
            if (event instanceof NavigationEnd) {
                setTimeout(() => {
                    this.collapseNavIfSmallScreen();
                    window.scrollTo(0, 0);

                    $el.find('a[href="#"]').on('click', (e) => {
                        e.preventDefault();
                    });
                });
            }
        });

        this.$sidebar.on('mouseenter', this._sidebarMouseEnter.bind(this));
        this.$sidebar.on('mouseleave', this._sidebarMouseLeave.bind(this));

        this.checkNavigationState();

        this.$sidebar.on('click', () => {
            if (jQuery('app-portal').is('.nav-collapsed')) {
                this.expandNavigation();
            }
        });

        this.router.events.subscribe(() => {
            this.collapseNavIfSmallScreen();
            window.scrollTo(0, 0);
        });

        /*if ('ontouchstart' in window) {
            this.enableSwipeCollapsing();
        }*/

        this.$sidebar.find('.collapse').on('show.bs.collapse', function (e): void {
            // execute only if we're actually the .collapse element initiated event
            // return for bubbled events
            if (e.target !== e.currentTarget) { return; }

            let $triggerLink = jQuery(this).prev('[data-toggle=collapse]');
            jQuery($triggerLink.data('parent'))
                .find('.collapse.in').not(jQuery(this)).collapse('hide');
        })
            /* adding additional classes to navigation link li-parent
             for several purposes. see navigation styles */
            .on('show.bs.collapse', function (e): void {
                // execute only if we're actually the .collapse element initiated event
                // return for bubbled events
                if (e.target !== e.currentTarget) { return; }

                jQuery(this).closest('li').addClass('open');
            }).on('hide.bs.collapse', function (e): void {
                // execute only if we're actually the .collapse element initiated event
                // return for bubbled events
                if (e.target !== e.currentTarget) { return; }

                jQuery(this).closest('li').removeClass('open');
            });
    }

    closeToastMessage() {
        this.toastMessage = ['', 'success'];
    }

    // unsubscribing subscriptions
    ngOnDestroy() {
        Object.keys(this.subscriptions).forEach(property => {
            this.subscriptions[property].unsubscribe();
        })
    }
}

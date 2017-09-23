import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { AppConfig } from 'app/services/app.config'
import { RedingtonErrorService } from '../../services/redington.error.service'
import { PartnerService } from '../partner/partner.service';
import { InactivePartnerService } from '../../portal/inactive-partner/inactive-partner.service';
import { Router } from '@angular/router';
import { GlobalsService } from 'app/services/globals.service';
import { Subscription } from 'rxjs/Subscription';
import { CustomersService } from "../../services/customers.service";
declare var jQuery: any;
import { Angulartics2 } from 'angulartics2';
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  encapsulation: ViewEncapsulation.Emulated,
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {

  config: any;
  configFn: any;
  sortOptions: Object = {
    connectWith: '.widget-container',
    handle: 'header, .handle',
    cursor: 'move',
    iframeFix: false,
    items: '.widget:not(.locked)',
    opacity: 0.8,
    helper: 'original',
    revert: true,
    forceHelperSize: true,
    placeholder: 'widget widget-placeholder',
    forcePlaceholderSize: true,
    tolerance: 'pointer'
  };
  public offerdetails: any
  private errors: any
  private booleanshowpagecontent: boolean
  private showtileclassOption: boolean
  private totalActivatedPartner: any;
  private totalInActivatedPartner: any;
  private current_month_totalActivatedPartner: any;
  private last_month_totalActivatedPartner: any;
  private current_year: any;
  global_subscription: Subscription;
  private permissions: any;
  private showPartnerWidget: boolean = false;
  private showActivatedPartnerWidget: boolean = false;
  public chartoptions: any;
  public dateobject: any;
  public currentyear: any;
  public chartList: any
  public regpartnerobject: any;
  private showCustomerWidget: boolean = false;
  public overallCustomer: any;
  public currentMonthCount: any;
  public previousMonthCount: any;
  public customerchartoptions: any;
  public userData: any;
  public ordersCount: any;
  public pendingOrders: any;
  public orderChartOptions: any;
  public name: any;
  public partnerCredits: Array<any> = [];
  public creditLimit: any;
  public cloudChartReport: any;
  public saasChartReport: any;
  public totalOrderCount: any;
  public pendingOrderCount: any;
  public approvedOrderCount: any;
  public showOrderWidget: boolean = false;
  public widgetChartcloud: any;
  public awsDetails: any;
  public softLayerDetails: any;
  public azureDetails: any;
  public approvedOrders: any;
  public BusinessReportAWS: any
  public BusinessReportAzure: any;
  public BusinessReportSoftLayer: any;
  public azureExist: any;
  public awsExist: any;
  public softLayerExist: any;
  public businessWidget: boolean = false;
  public billingChart: any;
  public pendingSo: any;
  public saasBusinessChart: any;
  public isv_banner_url:string = ""
  constructor(
    config: AppConfig,
    private errorservice: RedingtonErrorService,
    private partnerService: PartnerService,
    private inactivePartnerService: InactivePartnerService,
    private router: Router,
    private globalService: GlobalsService,
    private customersService: CustomersService,
    private angulartics2: Angulartics2,
  ) {
    this.configFn = config;
    this.config = config.getConfig();
    this.globalService.user$.subscribe(data => this.userData = data)

    this.global_subscription = globalService.userPermissions$.subscribe(permissions => {
      this.permissions = permissions;


    });
  }

  ngOnInit() {
    // Recording for google analytics
    this.angulartics2.eventTrack.next({
      action: 'Dashboard',
      properties: {
        category: 'Page Views'
      }
    });

    jQuery('.widget-container').sortable(this.sortOptions);
   

  }
  changeLoaders() {
    //this.errorservice.stopLoading();
    this.errorservice.publisherrormsg(true, "Error message");
  }

}

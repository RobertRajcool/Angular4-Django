import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { GetApiurl } from 'app/parameters'
import {GlobalsService} from 'app/services'

// Services
import { PartnerService } from './../partner.service';
declare var saveAs: any;

@Component({
  selector: 'app-partner-list',
  templateUrl: './partner-list.component.html',
  styleUrls: ['./partner-list.component.scss']
})
export class PartnerListComponent implements OnInit {

    public fetchUrl: string = GetApiurl('partner_details/');
    public addButtonInfo: Object = {};
    public commonFilter: Object = {filterString: '', columnName:'company_name,jba_code,email,city',
        placeholder: 'Search by Company name / Dealer Code / Email / City'};
    public rows: Array<any> = [];
    public columns: Array<any> = [
        { title: 'Company name', name: 'company_name', sort: true},
        { title: 'Contact person', name: 'name', sort: false },
        { title: 'Mobile', name: 'mobile', sort: false },
        { title: 'Email', name: 'email', sort: false},
        { title: 'City', name: 'city', sort: true },
        { title: 'Reg. date', name: 'created_at', dateFormat: 'yMMMd', sort: false },
        { title: 'Dealer Code', name: 'jba_code', sort: true },
        { title: 'Activated date', name: 'activated_at', dateFormat: 'yMMMd', sort: true },
        { title: 'Actions', links: ['View']},
    ];
    public backend_report_fetchUrl:string = GetApiurl('partner_details/download_active_partner_list/')
    public backend_report_fetchUrl_active:string = GetApiurl('partner_details/download_active_partner_list/')

    public reportFilters: Array<any> = [
    ];
    config: Object = {};
    isAWSUser: boolean = false;

    constructor(private service: PartnerService, private router: Router, private gsService: GlobalsService) {
        this.gsService.user$.subscribe(data => {
            if (data) {
                if (data['vendor_category']) {
                    data['vendor_category'].forEach((item, index) => {
                        if (item.vendor_name == 'AWS') {
                            this.isAWSUser = true
                        }
                    });
                }
            }
        });
        if (this.isAWSUser){
            this.config= {
                buttons: {
                    'export-raw': ['AWS Partners', true, false]
                }
            };
        }
    }

    ngOnInit() {
    }

    eventListener(event: any) {
        if (event.data.action == 'View') {
                let url: string;
                if (event.data.row.status) {
                    url = "/app/partner/" + event.data['row']['id'];
                } else {
                    url = "/app/partner/" + event.data['row']['id'] + "/activate";
                }
                this.router.navigateByUrl(url);
            }
            //  else if(event.data.action == 'Edit') {
            //     let url : string;
            //     url = "/app/partner/"+ event.data['row']['id'] + "/edit";
            //     this.router.navigateByUrl(url);
            // }
            else if (event.data.action == 'Delete') {
                console.log('delete');
            }
    }
    // Download all aws partners as excel
    exportExcel_AWS_Partners() {
        this.config = {
            buttons: {
                'export-raw': ['AWS Partners', false, true]
            }
        };
        this.service.export_aws_active_partners()
            .subscribe((Result: any) => {
                // Downloading File
                saveAs(Result['data'],'aws_active_partners'+'.csv');
                this.config = {
                    buttons: {
                        'export-raw': ['AWS Partners', true, false]
                    }
                };
            }, Error => {
                console.log(Error);
                this.config = {
                    buttons: {
                        'export-raw': ['AWS Partners', true, false]
                    }
                };
                this.gsService.setToastMessage('Data Export Failed', 5000, 'danger');
            });

    }


}

import { Component, OnInit,Input } from '@angular/core';
import {ResponseContentType, Http, Headers} from "@angular/http";
import {RedConstants} from '../../classes/constants'
declare var saveAs:any
@Component({
    selector: 'app-red-excel-report',
    templateUrl: './red-excel-report.component.html',
    styleUrls: ['./red-excel-report.component.scss']
})
export class RedExcelReportComponent implements OnInit {
    @Input() backend_fetchUrl_excel: string;
    @Input() commonFilter_Excel: any;
    @Input() screenName:string
    constructor(private http:Http) { }

    ngOnInit() {

    }
    public downloadCSVFile(){
        this.downloadCSV().subscribe(
            (res) => {
                /*
                 if we want new window
                 var fileURL = URL.createObjectURL(res);
                 window.open(fileURL);*/
                 let curent_date = new Date()
                 let file_name = this.screenName +
                 '('+curent_date.getDate()+'-'+curent_date.getMonth() +'-'+curent_date.getFullYear()+')'
                saveAs(res,this.screenName+'.xlsx')
            }
        );


    }
    private constructURL(): string {
        let url = this.backend_fetchUrl_excel + '?reportstatus=' + RedConstants.EXCELREPORT_STATUS;
        if(this.commonFilter_Excel.length) {
            this.commonFilter_Excel.forEach((column:any) => {
                let encodevalue=encodeURIComponent(column.value)
                url += '&' + column.name + '=' + encodevalue;
            });
        }
        return url;
    }
    public downloadCSV(): any {
        let url=this.constructURL()
        let headers = new Headers();
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        return this.http.get(url,{  headers: headers,responseType: ResponseContentType.Blob }).map(
            (res) => {
                return new Blob([res.blob()], { type: 'application/pdf' })
            })
    }

}

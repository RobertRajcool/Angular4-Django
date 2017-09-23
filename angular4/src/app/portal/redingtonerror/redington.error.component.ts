/**
 * Created by robert on 17/2/17.
 */
import { Component, Input } from '@angular/core';

@Component({
    selector: 'redington-error-app',
    templateUrl: './redington.error.component.html',
    styles:[`
         .errormsgstyle
         {
          position: fixed;
          z-index: 6000;
          text-align: center;
          width: 75%;
          top: 63px;
          margin: 0px !important;
          font-size: 18px;
          color:red;
         
         }
         .errorMsg {
             font-weight: bolder;
         }
`]
})
export class RedingtonErrorComponent {
    private _errorMessage:string;
    private _showerrorMsgStatus:boolean
    constructor() {
    }

    @Input()
    set errorMsg(errorMsg:string) {
        if (errorMsg) {
            this._errorMessage = errorMsg;
        } else {
            this._errorMessage = "No Input";
        }
    }

    get errorMsg() {
        return this._errorMessage;
    }
    @Input()
    set showerrorMsgStatus(showerrorMsgStatus:boolean){
        if(showerrorMsgStatus){
            this._showerrorMsgStatus=true
        }
        else {
            this._showerrorMsgStatus=false

        }
    }

    get showerrorMsgStatus(){
        return this._showerrorMsgStatus;
    }


}

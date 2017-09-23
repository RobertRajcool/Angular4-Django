/**
 * Created by robert on 17/2/17.
 */
import {Injectable,Output,EventEmitter} from '@angular/core'
@Injectable()
export class RedingtonErrorService {
    @Output() redingtonerrorFunction: EventEmitter<any> = new EventEmitter();

    constructor() { }


    getEmittedValue()
    {
        return this.redingtonerrorFunction;
    }

    publisherrormsg(errorstatus, errordata) {
        let errordataandstatus = {
            statusvalue: errorstatus,
            errordata: errordata
        };
        this.redingtonerrorFunction.emit(errordataandstatus);
    }

}

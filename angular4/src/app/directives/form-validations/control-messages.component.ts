import { Component, Input } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import { ValidationService } from './validation.service';

@Component({
    selector: 'control-messages',
    template: `  
  <div *ngIf="errorMessage !== null" class="form-error">{{errorMessage}}</div>`
})
export class ControlMessagesComponent {
    @Input('control') control: FormControl;
    constructor() { }

    get errorMessage() {
        for (let propertyName in this.control.errors) {
            if (this.control.errors.hasOwnProperty(propertyName) && this.control.touched) {
                let errorMsg: string = ValidationService.getValidatorErrorMessage(propertyName, this.control.errors[propertyName], getControlName(this.control));

                if (errorMsg) return errorMsg;
                else return this.control.errors[propertyName];
            }
        }

        return null;
    }
}



// Find control name from FormControl ...............................................................
export const getControlName = (control: any) => {
    var controlName = null;
    var parent = control["_parent"];

    // only such parent, which is FormGroup, has a dictionary 
    // with control-names as a key and a form-control as a value
    if (parent instanceof FormGroup) {
        // now we will iterate those keys (i.e. names of controls)
        Object.keys(parent.controls).forEach((name) => {
            // and compare the passed control and 
            // a child control of a parent - with provided name (we iterate them all)
            if (control === parent.controls[name]) {
                // both are same: control passed to Validator
                //  and this child - are the same references
                controlName = name;
            }
        });
    }
    // we either found a name or simply return null
    return controlName;
}

export class ValidationService {

    static getValidatorErrorMessage(validatorName: string, validatorValue?: any, controlName?: string) {
        let parent
        let config = {
            'required': `Please enter ${ValidationService.formatControlName(controlName)}`,
            'invalidCreditCard': 'Please enter valid credit card number',
            'invalidEmailAddress': 'Please enter valid email address',
            'invalidPassword': 'Please enter valid password. Password must be at least 6 characters long, and contain a number.',
            'invalidAzureWindowsPassword': 'Password must be 12 characters long and must have 3 of the following: 1 lower case, 1 upper case, 1 number, 1 special character',
            'notEqual': `Entered ${controlName} doesn\'t match`,
            'minlength': `Minimum length ${validatorValue.requiredLength}`,
            'invalidPercentage': 'Value should be inbetween 0-100',
            'invalidEmailRecipients': 'Please enter valid email address. Multiple emails should be seperated by comma.',
            'invalidUrl': 'Please enter valid url.',
            'invalidPhoneNumber': 'Mobile number must be 10 digits.',
            'invalidNonEmptyList': 'Please select atleast one value.',
            'invalidPanNumber': 'PAN number must contain 10 digits',
            'invalidUserName': 'Please avoid space in username',
            'maxlength': `Maximum length ${validatorValue.requiredLength}`,
            'invalidInstanceName': 'Please enter valid name without space & special characters',
            'invalidMinimumLength': 'Name must be at least 4 characters long',
            'invalidBucketName' : 'Bucket name must be in lowercase letters'
        };

        return config[validatorName];
    }

    static formatControlName(name: string){
        if(name) return name.replace(/_/g, " ");
        else return "input";
    }

    static creditCardValidator(control) {
        // Visa, MasterCard, American Express, Diners Club, Discover, JCB
        if (control.value.match(/^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$/)) {
            return null;
        } else {
            return { 'invalidCreditCard': true };
        }
    }

    static emailValidator(control) {
        // RFC 2822 compliant regex
        if ((!control.value) || control.value.match(/[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/)) {
            return null;
        } else {
            return { 'invalidEmailAddress': true };
        }
    }

    static passwordValidator(control) {
        // {6,100}           - Assert password is between 6 and 100 characters
        // (?=.*[0-9])       - Assert a string has at least one number
        if (control.value.match(/^(?=.*[0-9])[a-zA-Z0-9!@#$%^&*]{6,100}$/)) {
            return null;
        } else {
            return { 'invalidPassword': true };
        }
    }

    static azureWindowsPasswordValidator(control) {
        // {6,100}           - Assert password is between 12 and 100 characters
        // (?=.*[0-9])       - Assert a string has at least one number
        // (?=.*[!@#$%^&*])  - Assert a special character 
        if (control.value.match(/^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{12,100}$/)) {
            return null;
        } else {
            return { 'invalidAzureWindowsPassword': true };
        }
    }

    static nameWithoutSpaceValidator(control) {
        if (control.value.match(/^[a-zA-Z0-9\-_]{0,40}$/)) {
            return null;
        } else {
            return { 'invalidInstanceName': true };
        }
    }

    static upperCaseValidator(control) {
        if (control.value.match(/^[a-z0-9\-_]{0,40}$/)) {
            return null;
        } else {
            return { 'invalidBucketName': true };
        }
    }

    static minimumLengthValidator(control) {
        if (control.value.match(/^.{4,40}$/)) {
            return null;
        } else {
            return { 'invalidMinimumLength': true };
        }
    }

    static percentageValidator(control) {
        // 0-100 percentage value is between 0 to 100
        if (control.value >= 0 && control.value <= 100) {
            return null;
        } else {
            return { 'invalidPercentage': true };
        }
    }

    static multipleEmailValidator(control) {
        // Multiple emails seperated by comma regex
        if (control.value.match(/(([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)(\s*,\s*|\s*$))+/)) {
            return null;
        }
        else {
            return { 'invalidEmailRecipients': true };
        }
    }

    static urlValidator(control) {
        // Url regex
        if (!control.value || control.value.match(/(http|ftp|https):\/\/[\w-]+(\.[\w-]+)+([\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?/)) {
            return null;
        }
        else {
            return { 'invalidUrl': true };
        }
    }

    static phoneValidator(control) {
        var phoneNumber = /^\d{10}$/;
        if (control.value!=null && control.value.match(phoneNumber) || null) {
            return null;
        }
        else {
            return { 'invalidPhoneNumber': true };
        }
    }

    static pancardValidator(control) {
        var pan_number = /^[a-zA-Z0-9_.-]*$/;
        if (control.value.match(pan_number) || null) {
            return null;
        }
        else {
            return { 'invalidPanNumber': true };
        }


    }

    static nonEmptylistValidator(control) {
        // Checks is array & has Minimum one item in array
        if (control.value instanceof Array && (control.value.length > 0)) {
            return null;
        }
        else {
            return { 'invalidNonEmptyList': true };
        }
    }

    static equalValidator(group) {
        // Checks all values of controls in group are equal
        let controlNames: Array<string> = Object.keys(group.value);
        let first: string = controlNames.splice(0, 1)[0];

        for (let controlName of controlNames) {
            if (group.controls[first].touched && group.controls[controlName].touched && group.value[controlName] != group.value[first]) {
                return { 'notEqual': true };
            }
        }
        return null;
    }

    static userNameValidator(control) {
        var regex = /[^A-Za-z0-9!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/g; //_@./#&+-
        if (!control.value.match(regex)) {
            return null;
        }
        else {
            return { 'invalidUserName': true };
        }
    }

}

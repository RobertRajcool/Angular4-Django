import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer} from '@angular/platform-browser';
var moment: any = require('moment');

// Capitalize pipe .....................................................................
@Pipe({ name: 'capitalize' })

export class CapitalizePipe implements PipeTransform {
    transform(value, args: string[]): any {
        if (value) return value[0].toUpperCase() + value.slice(1);
        else return value;
    }
}

// Title Case pipe ......................................................................
@Pipe({ name: 'title' })

export class TitleCasePipe implements PipeTransform {
    transform(value, args: string[]): any {
        if (value) return value[0].toUpperCase() + value.slice(1).toLowerCase();
        else return value;
    }
}

// Replaces uderscores into spaces pipe .....................................................................
@Pipe({ name: 'u_to_space' })

export class UnderscoreToSpacePipe implements PipeTransform {
    transform(value, args: string[]): any {
        if (value) {
            return value.replace(/_/g, ' ');
        }
        else return value;
    }
}

// Check char in string pipe ......................................................................
@Pipe({ name: 'str_contains' })

export class InStringPipe implements PipeTransform {
    transform(value, args: string[]): any {
        if (value && value != '') {
            if (value.indexOf(args) >= 0) return true;
        }
        return false;
    }
}

// Check value in comma seperated string pipe ......................................................
@Pipe({ name: 'in_comma_seperated' })

export class InCommaSeperatedPipe implements PipeTransform {
    transform(value, args: string[]): any {
        if (value) {
            value = value.split(',');
            if (value.indexOf(args.toString()) >= 0) return true;
        }
        return false;
    }
}

// Check element in array pipe ......................................................................
@Pipe({ name: 'array_contains' })

export class InArrayPipe implements PipeTransform {
    transform(value, args: string[]): any {
        if (value instanceof Array) { 
            if (value.indexOf(args) >= 0) return true;
        }
        return false;
    }
}

// Return keys in object pipe ......................................................................
@Pipe({ name: 'keys' })

export class KeysPipe implements PipeTransform {
    transform(value, args: string[]): any {
        return Object.keys(value);
    }
}

// Timeline datetime pipe ...........................................................................
@Pipe({ name: 'timeline_datetime' })

export class TimelineDateTimePipe implements PipeTransform {
    transform(value, args: string[]): any {
        return moment(value).fromNow();
    }
}

// Format datetime pipe ...........................................................................
@Pipe({ name: 'format_datetime' })

export class FormatDateTimePipe implements PipeTransform {
    private monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    private monthShortNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    transform(value, args: string): any {
        value = new Date(value);
        switch (args) {
            case 'dd mmm yyyy hh:mm':
                return value.getDate() + ' ' + this.monthShortNames[value.getMonth()] + ' ' + value.getFullYear() + ' ' + value.getHours() + ':' + (value.getMinutes() < 10 ? '0' : '') + value.getMinutes();
            default: return value;
        }
    }
}

// Currency format pipe ..........................................................................
const PADDING = "000000";

@Pipe({ name: "Currency" })
export class CurrencyPipe implements PipeTransform {

    private DECIMAL_SEPARATOR: string;
    private THOUSANDS_SEPARATOR: string;

    constructor() {
        // TODO comes from configuration settings
        this.DECIMAL_SEPARATOR = ".";
        this.THOUSANDS_SEPARATOR = ",";
    }

    transform(
        value: number | string, 
        fractionSize: number = 2, 
        currencyFormat: string = 'INR', 
        symbolDisplay: boolean = false
        ): string {
        
        let [integer, fraction = ""] = (value || 0).toString()
            .split(this.DECIMAL_SEPARATOR);

        fraction = fractionSize > 0
            ? this.DECIMAL_SEPARATOR + (fraction + PADDING).substring(0, fractionSize)
            : "";
        
        switch (currencyFormat) {
            case "INR":  // Indian Rupee
                integer = integer.replace(/(\d)(?=(\d\d)+\d$)/g, `$1${this.THOUSANDS_SEPARATOR}`);
                if(symbolDisplay) integer = `₹ ${integer}`;
                break;
            case "USD":  // United States Dollar
                integer = integer.replace(/(\d)(?=(\d{3})+\d{0}$)/g, `$1${this.THOUSANDS_SEPARATOR}`);
                if(symbolDisplay) integer = `$ ${integer}`;
                break;
            default:    // Default (INR)
                integer = integer.replace(/(\d)(?=(\d\d)+\d$)/g, `$1${this.THOUSANDS_SEPARATOR}`);
                if(symbolDisplay) integer = `₹ ${integer}`;
                break;
        }

        return integer + fraction;
    }

    parse(value: string, fractionSize: number = 2): string {
        let [integer, fraction = ""] = (value || "").split(this.DECIMAL_SEPARATOR);

        integer = integer.replace(new RegExp(this.THOUSANDS_SEPARATOR, "g"), "");

        fraction = parseInt(fraction, 10) > 0 && fractionSize > 0
            ? this.DECIMAL_SEPARATOR + (fraction + PADDING).substring(0, fractionSize)
            : "";

        return integer + fraction;
    }

}

@Pipe({ name: 'safe' })
export class SafePipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}
  transform(url) {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }
}

@Pipe({ name: 'safeHTML' })
export class SafeHTMLPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}
  transform(url) {
    return this.sanitizer.bypassSecurityTrustHtml(url);
  }
}

@Pipe({name: 'round'})
export class RoundPipe implements PipeTransform {
    /**
     *
     * @param value
     * @returns {number}
     */
    transform(value: number): number {
        return Math.round(value);
    }
}
// split even and odd rows
@Pipe({ name: "row" })
export class RowPipe implements PipeTransform {
  // input is an array of any
  // mod is the modulo, every mod items, create a row
  transform(input: any[], mod: number): any[][] {
    return input.reduce((previous, next, index) => {
      if (index % mod === 0)
        previous.push([next]);
      else
        previous[previous.length - 1].push(next);
      return previous;
    }, <any[][]>[]);
  }
}

@Pipe({
  name: 'limitTo'
})
export class TruncatePipe {
  transform(value: string, args: string) : string {
    // let limit = args.length > 0 ? parseInt(args[0], 10) : 10;
    // let trail = args.length > 1 ? args[1] : '...';
    let limit = args ? parseInt(args, 10) : 10;
    let trail = '...';

    return value.length > limit ? value.substring(0, limit) + trail : value;
  }
}
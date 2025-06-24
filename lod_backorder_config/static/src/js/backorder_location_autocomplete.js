import { AutoComplete } from "@web/core/autocomplete/autocomplete";


export class BackOrderLocationAutocomplete extends AutoComplete {

    setup() {
        super.setup();
        
    }
    async loadSources(useInput) {
        this.sources = [];
        this.state.activeSourceOption = null;
        const proms = [];
        for (const pSource of this.props.sources) {
            const source = this.makeSource(pSource);
            this.sources.push(source);

            var options = this.loadOptions(
                pSource.options,
                useInput ? this.inputRef.el.value.trim() : ""
            );
            if (this.inputRef.el.value){
            options = options.filter((option) => {
                    return option.label.includes(this.inputRef.el.value);
                  });
            }
            if (options instanceof Promise) {
                source.isLoading = true;
                const prom = options.then((options) => {
                    source.options = options.map((option) => this.makeOption(option));
                    source.isLoading = false;
                    this.state.optionsRev++;
                });
                proms.push(prom);
            } else {
                source.options = options.map((option) => this.makeOption(option));
            }
        }

        await Promise.all(proms);
        this.navigate(0);
    }


}


function clipText(text: string, maxLength: number = 10000): string {
    if (text.length > maxLength) {
        return text.slice(0, maxLength) + '...';
    }
    return text;
}

export {clipText};
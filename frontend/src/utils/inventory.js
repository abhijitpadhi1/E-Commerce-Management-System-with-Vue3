export function getStockStatus(stock) {
    if (stock <= 0) {
        return {
            label: 'Out of Stock',
            className: 'text-danger',
        }
    }

    if (stock <= 5) {
        return {
            label: `Only ${stock} left`,
            className: 'text-warning',
        }
    }

    return {
        label: 'In Stock',
        className: 'text-success',
    }
}
/// Shared utility functions used across multiple modules.
/// Find the largest byte index `<= index` that lies on a UTF-8 char boundary.
///
/// Equivalent to the nightly-only `str::floor_char_boundary()`.
/// Returns `s.len()` when `index >= s.len()`.
pub fn floor_char_boundary(s: &str, index: usize) -> usize {
    if index >= s.len() {
        s.len()
    } else {
        let mut i = index;
        while i > 0 && !s.is_char_boundary(i) {
            i -= 1;
        }
        i
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_floor_char_boundary_ascii() {
        assert_eq!(floor_char_boundary("hello", 3), 3);
        assert_eq!(floor_char_boundary("hello", 10), 5); // beyond len
        assert_eq!(floor_char_boundary("hello", 0), 0);
    }

    #[test]
    fn test_floor_char_boundary_multibyte() {
        let s = "caf\u{00e9}"; // 5 bytes: c(1) a(1) f(1) é(2)
        assert_eq!(floor_char_boundary(s, 5), 5); // full string
        assert_eq!(floor_char_boundary(s, 4), 3); // mid-'é', rounds down
        assert_eq!(floor_char_boundary(s, 3), 3); // start of 'é'
    }

    #[test]
    fn test_floor_char_boundary_cjk() {
        let s = "\u{4e16}\u{754c}"; // 6 bytes: 世(3) 界(3)
        assert_eq!(floor_char_boundary(s, 6), 6);
        assert_eq!(floor_char_boundary(s, 5), 3); // mid-second char
        assert_eq!(floor_char_boundary(s, 4), 3);
        assert_eq!(floor_char_boundary(s, 3), 3);
        assert_eq!(floor_char_boundary(s, 2), 0); // mid-first char
        assert_eq!(floor_char_boundary(s, 1), 0);
    }

    #[test]
    fn test_floor_char_boundary_empty() {
        assert_eq!(floor_char_boundary("", 0), 0);
        assert_eq!(floor_char_boundary("", 5), 0);
    }
}

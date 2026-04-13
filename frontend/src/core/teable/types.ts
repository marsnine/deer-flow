export interface TeableSpace {
  id: string;
  name: string;
  role?: string;
}

export interface TeableBase {
  id: string;
  name: string;
  spaceId?: string;
}

export interface TeableTable {
  id: string;
  name: string;
  description?: string;
}

export interface TeableConfig {
  base_id: string;
  public_url: string;
}

export interface TeableShareView {
  embed_url: string;
  view_id: string;
  share_id: string;
}
